import React, { useState, useRef, useEffect } from 'react';
import {
  View, Text, StyleSheet, TextInput, FlatList, KeyboardAvoidingView,
  Platform, ActivityIndicator, TouchableOpacity, Alert, Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Audio } from 'expo-av';
import { StatusBar } from 'expo-status-bar';
import { useLocalSearchParams } from 'expo-router';

// Imports
import { ENDPOINTS } from '../../constants/config';
import { getOrCreateUserId } from '../../utils/user_manager';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatScreen() {
  const params = useLocalSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  
  // Tracks the current active thread
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);

  const flatListRef = useRef<FlatList>(null);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  // INITIALIZATION
  useEffect(() => {
    const init = async () => {
      const id = await getOrCreateUserId();
      setUserId(id);

      if (params.conversationId) {
        if (params.conversationId === 'new') {
          // Fresh Start
          setMessages([]);
          setActiveConversationId(null);
        } else {
          // Load Old Chat
          const convId = parseInt(params.conversationId as string, 10);
          setActiveConversationId(convId);
          loadConversationHistory(convId);
        }
      }
    };
    init();
  }, [params.conversationId]);

  const loadConversationHistory = async (id: number) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${ENDPOINTS.GET_CHAT}/${id}`);
      const data = await res.json();
      setMessages(data.messages || []);
    } catch (e) {
      console.error("Failed to load history", e);
    } finally {
      setIsLoading(false);
    }
  };

  // Cleanup sound
  useEffect(() => {
    return sound ? () => { sound.unloadAsync(); } : undefined;
  }, [sound]);


  // AUDIO LOGIC

  async function playResponseAudio(text: string) {
    try {
        if (sound) await sound.unloadAsync();
        
        // Don't speak very short texts unless they are questions
        if (text.split(' ').length < 2 && !text.includes('?')) return;

        const response = await fetch(ENDPOINTS.SYNTHESIZE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text }),
        });

        if (!response.ok) return;
        const result = await response.json();

        if (result.url) {
            const { sound: newSound } = await Audio.Sound.createAsync(
                { uri: result.url }, 
                { shouldPlay: true }
            );
            setSound(newSound);
        }
    } catch (e) { 
        console.error("TTS Error:", e); 
    }
  }

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Microphone permission is required.');
        return;
      }
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      const { recording } = await Audio.Recording.createAsync(
         Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    setRecording(null);
    await recording.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({ allowsRecordingIOS: false });
    
    const uri = recording.getURI();
    if (uri) {
      transcribeAudio(uri);
    }
  };

  const transcribeAudio = async (fileUri: string) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('audio_file', {
      uri: fileUri,
      name: 'recording.m4a',
      type: 'audio/m4a',
    } as any);

    try {
      const response = await fetch(ENDPOINTS.TRANSCRIBE, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('STT Failed');
      
      const result = await response.json();
      if (result.text) {
        handleSend(result.text, 'speech');
      }
    } catch (error) {
      console.error('Transcription Error:', error);
      Alert.alert('Error', 'Could not understand audio.');
      setIsLoading(false);
    }
  };


  // CHAT LOGIC

  const handleSend = async (textToSend: string, source: 'text' | 'speech') => {
    if (textToSend.trim() === '' || !userId) return;

    const userMessage: Message = { role: 'user', content: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setInputText('');

    try {
      const isNewChat = (params.conversationId === 'new' && activeConversationId === null);

      const payload = {
        user_id: userId,
        message: textToSend,
        conversation_id: activeConversationId,
        force_new: isNewChat 
      };

      const response = await fetch(ENDPOINTS.CHAT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Backend Error');

      const data = await response.json();

      if (data.conversation_id) {
        setActiveConversationId(data.conversation_id);
      }

      const aiMessage: Message = { role: 'assistant', content: data.content };
      setMessages((prev) => [...prev, aiMessage]);

      if (source === 'speech') {
        playResponseAudio(data.content);
      }

    } catch (error) {
      console.error('Chat Error:', error);
      setMessages((prev) => [...prev, { role: 'assistant', content: "Connection failed." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}>
      <StatusBar style="dark" />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'padding'}
        style={styles.container}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 150 : 100}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          style={styles.chatLog}
          contentContainerStyle={styles.chatLogContent}
          renderItem={({ item }) => (
            <View style={[styles.bubble, item.role === 'user' ? styles.userBubble : styles.aiBubble]}>
              <Text style={item.role === 'user' ? styles.userText : styles.aiText}>{item.content}</Text>
            </View>
          )}
          keyExtractor={(_, index) => index.toString()}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
        />

        {isLoading && (
          <View style={styles.typingIndicator}>
            <Text style={styles.typingText}>{recording ? 'Listening...' : 'Rod is typing...'}</Text>
            <ActivityIndicator size="small" color="#888" />
          </View>
        )}

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Message..."
            onSubmitEditing={() => handleSend(inputText, 'text')}
          />
          
          <TouchableOpacity
            style={styles.iconButton}
            onPress={() => handleSend(inputText, 'text')}
            disabled={isLoading || inputText.length === 0}
          >
            <Image 
              source={require('../../assets/icons/send_icon.png')} 
              style={[styles.icon, inputText.length === 0 && styles.iconDisabled]} 
            />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.iconButton}
            onPressIn={startRecording}
            onPressOut={stopRecording}
            disabled={isLoading}
          >
            <Image 
              source={require('../../assets/icons/mic_icon.png')} 
              style={[styles.icon, recording && styles.iconRecording]} 
            />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: 'white' },
  container: { flex: 1 },
  chatLog: { flex: 1 },
  chatLogContent: { padding: 10, paddingBottom: 20 },
  bubble: { padding: 12, borderRadius: 18, marginBottom: 10, maxWidth: '80%' },
  userBubble: { backgroundColor: '#007AFF', alignSelf: 'flex-end', borderBottomRightRadius: 2 },
  aiBubble: { backgroundColor: '#F2F2F7', alignSelf: 'flex-start', borderBottomLeftRadius: 2 },
  userText: { color: 'white', fontSize: 16 },
  aiText: { color: 'black', fontSize: 16 },
  typingIndicator: { flexDirection: 'row', alignItems: 'center', padding: 10, paddingLeft: 20 },
  typingText: { color: '#8E8E93', fontStyle: 'italic', marginRight: 8 },
  inputContainer: { flexDirection: 'row', paddingHorizontal: 10, paddingVertical: 8, borderTopWidth: 1, borderColor: '#CCC', backgroundColor: 'white', alignItems: 'center' },
  textInput: { flex: 1, height: 40, borderColor: '#DDD', borderWidth: 1, borderRadius: 20, paddingHorizontal: 15 },
  iconButton: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center', marginLeft: 5 },
  icon: { width: 24, height: 24, tintColor: '#007AFF' },
  iconDisabled: { tintColor: '#CCC' },
  iconRecording: { tintColor: 'red' }
});