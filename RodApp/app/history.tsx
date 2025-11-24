import React, { useEffect, useState } from 'react';
import { 
  View, Text, StyleSheet, FlatList, TouchableOpacity, Image, 
  Alert, TextInput, Modal, KeyboardAvoidingView, Platform 
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ENDPOINTS } from '../constants/config';
import { getOrCreateUserId } from '../utils/user_manager';

interface Conversation {
  id: number;
  date: string;
  title: string;
}

export default function HistoryScreen() {
  const router = useRouter();
  const [history, setHistory] = useState<Conversation[]>([]);
  const [userId, setUserId] = useState<string | null>(null);
  
  // Edit Modal State
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [editText, setEditText] = useState('');

  const loadHistory = async () => {
    try {
      const userData = await getOrCreateUserId();
      
      // Handle both Object and String cases safely
      const idString = typeof userData === 'object' ? userData.id : userData;
      setUserId(idString);

      const response = await fetch(`${ENDPOINTS.HISTORY}/${idString}`);
      const data = await response.json();
      
      setHistory(data.conversations || []);
    } catch (e) {
      console.error("Failed to load history", e);
    }
  };

  // Initial Load
  useEffect(() => {
    loadHistory();
  }, []);

  const handleSelect = (id: number) => {
    router.dismiss(); 
    router.push({ pathname: '/(tabs)/chat', params: { conversationId: id } });
  };

  const handleNewChat = () => {
    router.dismiss();
    router.push({ pathname: '/(tabs)/chat', params: { conversationId: 'new' } });
  };

  // Open the name edit window
  const openEditModal = (item: Conversation) => {
    setSelectedId(item.id);
    setEditText(item.title);
    setModalVisible(true);
  };

  const saveTitle = async () => {
    if (!selectedId) return;
    try {
        await fetch(`${ENDPOINTS.CONVERSATIONS}/${selectedId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title: editText })
        });
        setModalVisible(false);
        loadHistory(); // Refresh list
    } catch (e) {
        Alert.alert("Error", "Could not rename chat.");
    }
  };

  const renderItem = ({ item }: { item: Conversation }) => (
    <View style={styles.itemContainer}>
      <TouchableOpacity style={styles.itemContent} onPress={() => handleSelect(item.id)}>
          <View>
              <Text style={styles.itemTitle} numberOfLines={1}>
                {item.title || "Untitled Conversation"}
              </Text>
              <Text style={styles.itemDate}>
                {new Date(item.date).toLocaleDateString()}
              </Text>
          </View>
      </TouchableOpacity>
      
      <TouchableOpacity style={styles.editBtn} onPress={() => openEditModal(item)}>
         <Image 
            source={require('../assets/icons/edit_icon.png')} 
            style={styles.editIcon} 
         />
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>History</Text>
        <TouchableOpacity onPress={() => router.back()}>
             <Text style={styles.closeText}>Close</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.newChatBtn} onPress={handleNewChat}>
        <Text style={styles.newChatText}>+ Start New Conversation</Text>
      </TouchableOpacity>

      <FlatList
        data={history}
        renderItem={renderItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={{ padding: 20 }}
      />

      <Modal
        animationType="fade"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <KeyboardAvoidingView 
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.modalOverlay}
        >
          <View style={styles.modalView}>
            <Text style={styles.modalTitle}>Rename Conversation</Text>
            <TextInput
                style={styles.modalInput}
                value={editText}
                onChangeText={setEditText}
                autoFocus={true}
            />
            <View style={styles.modalButtons}>
                <TouchableOpacity 
                    style={[styles.modalBtn, styles.cancelBtn]} 
                    onPress={() => setModalVisible(false)}
                >
                    <Text style={styles.cancelText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                    style={[styles.modalBtn, styles.saveBtn]} 
                    onPress={saveTitle}
                >
                    <Text style={styles.saveText}>Save</Text>
                </TouchableOpacity>
            </View>
          </View>
        </KeyboardAvoidingView>
      </Modal>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7' },
  header: { flexDirection: 'row', justifyContent: 'space-between', padding: 20, alignItems: 'center' },
  title: { fontSize: 28, fontWeight: 'bold' },
  closeText: { color: '#007AFF', fontSize: 16 },
  newChatBtn: {
    backgroundColor: '#007AFF',
    margin: 20,
    padding: 15,
    borderRadius: 12,
    alignItems: 'center',
  },
  newChatText: { color: 'white', fontWeight: 'bold', fontSize: 16 },
  itemContainer: {
    flexDirection: 'row',
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 12,
    marginBottom: 10,
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  itemContent: { flex: 1 },
  itemTitle: { fontSize: 16, fontWeight: '600', marginBottom: 4 },
  itemDate: { fontSize: 12, color: '#8E8E93' },
  editBtn: { padding: 5 },
  editIcon: { width: 20, height: 20, tintColor: '#C7C7CC' },
  
  // Modal Styles
  modalOverlay: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(0,0,0,0.5)' // Dims the background
  },
  modalView: {
      width: '80%',
      backgroundColor: 'white',
      borderRadius: 20,
      padding: 25,
      alignItems: 'center',
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.25,
      shadowRadius: 4,
      elevation: 5
  },
  modalTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15 },
  modalInput: {
      width: '100%',
      borderBottomWidth: 1,
      borderColor: '#CCC',
      padding: 8,
      fontSize: 16,
      marginBottom: 20
  },
  modalButtons: { flexDirection: 'row', width: '100%', justifyContent: 'space-between' },
  modalBtn: {
      flex: 1,
      padding: 10,
      alignItems: 'center',
      borderRadius: 8
  },
  cancelBtn: { marginRight: 10 },
  saveBtn: { backgroundColor: '#007AFF' },
  cancelText: { color: 'red', fontWeight: 'bold' },
  saveText: { color: 'white', fontWeight: 'bold' }
});