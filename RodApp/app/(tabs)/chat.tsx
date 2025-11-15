import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  TouchableOpacity, 
  Alert,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context'; 
import { Audio } from 'expo-av';
import { StatusBar } from 'expo-status-bar';

const API_URL = 'http://172.16.234.107:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  useEffect(() => {
    return sound ? () => { sound.unloadAsync(); } : undefined;
  }, [sound]); 

  
  async function playAudio(text: string) {
    if (sound) await sound.unloadAsync();
    if (text.split(' ').length < 2 && !text.includes('?')) return; 
    try {
      const response = await fetch(`${API_URL}/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text }),
      });
      if (!response.ok) throw new Error('Synthesis failed');
      const result = await response.json();
      if (!result.url) throw new Error('No audio URL returned');
      
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: result.url },
        { shouldPlay: true } 
      );
      setSound(newSound); 
    } catch (error) {
      console.error('Failed to play audio:', error);
    }
  }

  const handleSend = async (textToSend: string, source: 'text' | 'speech') => {
    if (textToSend.trim() === '') return;

    const userMessage: Message = { role: 'user', content: textToSend };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setIsLoading(true);
    setInputText('');
    
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ history: newMessages }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const aiResponse: Message = await response.json();
      setMessages((prevMessages) => [...prevMessages, aiResponse]);
      
      if (source === 'speech') {
        playAudio(aiResponse.content);
      }
    } catch (error) {
      console.error('Error fetching AI response:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: "Sorry, I couldn't connect. Please try again."
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Please grant microphone permissions in your settings.');
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
      const response = await fetch(`${API_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Transcription network response was not ok');
      const result = await response.json();
      if (result.text) {
        handleSend(result.text, 'speech'); 
      } else {
        throw new Error(result.error || 'Transcription failed');
      }
    } catch (error) {
      console.error('Error transcribing audio:', error);
      Alert.alert('Error', 'Could not transcribe audio.');
      setIsLoading(false); 
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top']}> 
      <StatusBar style="dark" /> 

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'padding'}
        style={styles.container}
        // IOS FIX: Offset for Header (~60) + Tab Bar (90) = 150
        keyboardVerticalOffset={Platform.OS === 'ios' ? 150 : 100}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          style={styles.chatLog} 
          contentContainerStyle={styles.chatLogContent} 
          renderItem={({ item }) => (
            <View 
              style={[
                styles.bubble, 
                item.role === 'user' ? styles.userBubble : styles.aiBubble
              ]}
            >
              <Text 
                style={item.role === 'user' ? styles.userText : styles.aiText}
              >
                {item.content}
              </Text>
            </View>
          )}
          keyExtractor={(item, index) => index.toString()}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd()} 
        />

        {isLoading && (
          <View style={styles.typingIndicator}>
            <Text style={styles.typingText}>
              {recording ? 'Transcribing...' : 'Rod is typing...'}
            </Text>
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
  chatLogContent: { padding: 10 },
  bubble: {
    padding: 12,
    borderRadius: 20,
    marginBottom: 10,
    maxWidth: '80%',
  },
  userBubble: { backgroundColor: '#007AFF', alignSelf: 'flex-end' },
  aiBubble: { backgroundColor: '#E5E5EA', alignSelf: 'flex-start' },
  userText: { color: 'white' },
  aiText: { color: 'black' },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    paddingLeft: 20,
  },
  typingText: {
    color: '#888',
    fontStyle: 'italic',
    marginRight: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderColor: '#CCC',
    backgroundColor: 'white',
    alignItems: 'center', 
  },
  textInput: {
    flex: 1,
    height: 40,
    borderColor: '#DDD',
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 15,
  },
  iconButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 5,
  },
  icon: {
    width: 24,
    height: 24,
    tintColor: '#007AFF', 
  },
  iconDisabled: {
    tintColor: '#CCC', 
  },
  iconRecording: {
    tintColor: 'red', 
  }
});