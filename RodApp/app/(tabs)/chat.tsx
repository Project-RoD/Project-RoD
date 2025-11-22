import React, { useState, useRef, useEffect, useLayoutEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, TextInput, FlatList, KeyboardAvoidingView,
  Platform, ActivityIndicator, TouchableOpacity, Alert, Image, Modal, ScrollView
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Audio } from 'expo-av';
import { StatusBar } from 'expo-status-bar';
import { useLocalSearchParams, useNavigation, useRouter, useFocusEffect } from 'expo-router';
import { DeviceEventEmitter } from 'react-native';
import { ENDPOINTS } from '../../constants/config';
import { getOrCreateUserId } from '../../utils/user_manager';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface FeedbackItem {
  user_text: string;
  correction: string;
  explanation: string;
}

export default function ChatScreen() {
  const params = useLocalSearchParams();
  const router = useRouter();
  const navigation = useNavigation();
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);

  const flatListRef = useRef<FlatList>(null);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  const [feedbackVisible, setFeedbackVisible] = useState(false);
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [loadingFeedback, setLoadingFeedback] = useState(false);

  // 1. HEADER INJECTION
  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <View style={styles.headerRightContainer}>
          <TouchableOpacity onPress={openFeedback} style={styles.headerButton}>
             <Image 
                source={require('../../assets/icons/lightbulb_icon.png')} 
                style={styles.headerIconOriginal} 
             />
          </TouchableOpacity>
          <TouchableOpacity onPress={() => router.push('/profile')}>
             <Image 
                source={require('../../assets/icons/profile_icon.png')} 
                style={styles.profileIcon} 
             />
          </TouchableOpacity>
        </View>
      ),
    });
  }, [navigation, activeConversationId]);

  // 2. INIT & LOAD
  useFocusEffect(
    useCallback(() => {
      const init = async () => {
        const userData = await getOrCreateUserId();
        const idString = typeof userData === 'object' ? userData.id : userData;
        setUserId(idString);

        if (params.conversationId) {
          if (params.conversationId === 'new') {
            setMessages([]);
            setFeedbackList([]);
            setActiveConversationId(null);
          } else {
            const convId = parseInt(params.conversationId as string, 10);
            
            if (activeConversationId !== convId) {
                setMessages([]); 
                setFeedbackList([]);
                setActiveConversationId(convId);
                loadConversationHistory(convId);
            }
          }
        }
      };
      init();
    }, [params.conversationId])
  );

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

  // 3. FEEDBACK
  const openFeedback = async () => {
    setFeedbackVisible(true);
    if (!activeConversationId) return;

    setLoadingFeedback(true);
    try {
      const baseUrl = ENDPOINTS.CHAT.replace('/chat', ''); 
      const res = await fetch(`${baseUrl}/feedback/${activeConversationId}`);
      const data = await res.json();
      setFeedbackList(data.feedback || []);
    } catch (e) {
      Alert.alert("Error", "Could not fetch feedback.");
    } finally {
      setLoadingFeedback(false);
    }
  };

  // 4. AUDIO & SEND
  useEffect(() => { return sound ? () => { sound.unloadAsync(); } : undefined; }, [sound]);

  async function playResponseAudio(text: string) {
    try {
        if (sound) await sound.unloadAsync();
        if (text.split(' ').length < 2 && !text.includes('?')) return;
        const response = await fetch(ENDPOINTS.SYNTHESIZE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text }),
        });
        if (!response.ok) return;
        const result = await response.json();
        if (result.url) {
            const { sound: newSound } = await Audio.Sound.createAsync({ uri: result.url }, { shouldPlay: true });
            setSound(newSound);
        }
    } catch (e) { console.error(e); }
  }

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Microphone permission is required.');
        return;
      }
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const { recording } = await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      setRecording(recording);
    } catch (err) { console.error(err); }
  };

  const stopRecording = async () => {
    if (!recording) return;
    setRecording(null);
    await recording.stopAndUnloadAsync();
    await Audio.setAudioModeAsync({ allowsRecordingIOS: false });
    const uri = recording.getURI();
    if (uri) transcribeAudio(uri);
  };

  const transcribeAudio = async (fileUri: string) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('audio_file', { uri: fileUri, name: 'recording.m4a', type: 'audio/m4a' } as any);
    try {
      const response = await fetch(ENDPOINTS.TRANSCRIBE, { method: 'POST', body: formData });
      if (!response.ok) throw new Error('STT Failed');
      const result = await response.json();
      if (result.text) handleSend(result.text, 'speech');
    } catch (error) {
      Alert.alert('Error', 'Could not understand audio.');
      setIsLoading(false);
    }
  };

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

      // Send Signal to Header
      DeviceEventEmitter.emit('streakUpdate');

      const data = await response.json();

      if (data.conversation_id) setActiveConversationId(data.conversation_id);

      const aiMessage: Message = { role: 'assistant', content: data.content };
      setMessages((prev) => [...prev, aiMessage]);

      if (source === 'speech') playResponseAudio(data.content);

    } catch (error) {
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
          <TouchableOpacity style={styles.iconButton} onPress={() => handleSend(inputText, 'text')}>
            <Image source={require('../../assets/icons/send_icon.png')} style={styles.icon} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.iconButton} onPressIn={startRecording} onPressOut={stopRecording}>
            <Image source={require('../../assets/icons/mic_icon.png')} style={[styles.icon, recording && styles.iconRecording]} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      <Modal
        animationType="slide"
        transparent={true}
        visible={feedbackVisible}
        onRequestClose={() => setFeedbackVisible(false)}
      >
        <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
                <View style={styles.modalHeader}>
                    <Text style={styles.modalTitle}>Conversation Feedback!</Text>
                    <TouchableOpacity onPress={() => setFeedbackVisible(false)}>
                        <Text style={styles.closeText}>Close</Text>
                    </TouchableOpacity>
                </View>
                
                {loadingFeedback ? (
                    <ActivityIndicator size="large" color="#007AFF" style={{marginTop: 20}} />
                ) : (
                    <ScrollView contentContainerStyle={{paddingBottom: 20}}>
                        {feedbackList.length === 0 ? (
                            <Text style={styles.emptyText}>No grammar errors found yet! 🎉</Text>
                        ) : (
                            feedbackList.map((item, index) => (
                                <View key={index} style={styles.feedbackCard}>
                                    <Text style={styles.fbOriginal}>"{item.user_text}"</Text>
                                    <Text style={styles.fbCorrection}>✅ {item.correction}</Text>
                                    <Text style={styles.fbExplanation}>ℹ️ {item.explanation}</Text>
                                </View>
                            ))
                        )}
                    </ScrollView>
                )}
            </View>
        </View>
      </Modal>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: 'white' },
  container: { flex: 1 },

  // HEADER
  headerRightContainer: { flexDirection: 'row', alignItems: 'center', marginRight: 15 },
  headerButton: { marginRight: 15 },
  headerIconOriginal: { width: 28, height: 28 }, 
  profileIcon: { width: 30, height: 30, tintColor: 'black' },

  // CHAT
  chatLog: { flex: 1 },
  chatLogContent: { padding: 10, paddingBottom: 20 },
  bubble: { padding: 12, borderRadius: 18, marginBottom: 10, maxWidth: '80%' },
  userBubble: { backgroundColor: '#007AFF', alignSelf: 'flex-end', borderBottomRightRadius: 2 },
  aiBubble: { backgroundColor: '#F2F2F7', alignSelf: 'flex-start', borderBottomLeftRadius: 2 },
  userText: { color: 'white', fontSize: 16 },
  aiText: { color: 'black', fontSize: 16 },
  
  // INDICATOR
  typingIndicator: { padding: 10, paddingLeft: 20, flexDirection: 'row', alignItems: 'center', width: '100%' },
  typingText: { color: '#333', fontSize: 14, marginRight: 8, fontWeight: '500' },
  
  // INPUT
  inputContainer: { flexDirection: 'row', padding: 10, borderTopWidth: 1, borderColor: '#E5E5EA', backgroundColor: 'white', alignItems: 'center' },
  textInput: { flex: 1, height: 40, backgroundColor: '#F2F2F7', borderRadius: 20, paddingHorizontal: 15 },
  iconButton: { width: 40, height: 40, justifyContent: 'center', alignItems: 'center', marginLeft: 5 },
  icon: { width: 24, height: 24, tintColor: '#007AFF' },
  iconRecording: { tintColor: 'red' },

  // MODAL
  modalOverlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.3)' },
  modalContent: { height: '60%', backgroundColor: 'white', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  modalTitle: { fontSize: 20, fontWeight: 'bold' },
  closeText: { color: '#007AFF', fontSize: 16, fontWeight: 'bold' },
  emptyText: { textAlign: 'center', color: '#888', marginTop: 30, fontSize: 16 },
  
  // CARDS
  feedbackCard: { backgroundColor: '#F9F9F9', padding: 15, borderRadius: 10, marginBottom: 15, borderWidth: 1, borderColor: '#EEE' },
  fbOriginal: { fontSize: 16, color: '#FF3B30', textDecorationLine: 'line-through', marginBottom: 5 },
  fbCorrection: { fontSize: 16, color: '#34C759', fontWeight: 'bold', marginBottom: 5 },
  fbExplanation: { fontSize: 14, color: '#555' }
});