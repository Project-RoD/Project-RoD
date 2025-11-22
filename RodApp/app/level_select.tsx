import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ENDPOINTS } from '../constants/config';
import { getOrCreateUserId } from '../utils/user_manager';

export default function LevelSelectScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const setLevel = async (level: string) => {
    setLoading(true);
    try {
      // 1. Get the full object
      const userData = await getOrCreateUserId();
      
      // 2. Extract the ID string safely (Handle both Object and String cases to be safe)
      const userId = typeof userData === 'object' ? userData.id : userData;

      // 3. Fetch using the Constant DIRECTLY (No extra /user/level string)
      await fetch(ENDPOINTS.USER_LEVEL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, level: level }),
      });
      
      router.dismiss();
    } catch (error) {
      console.error("Failed to set level", error);
      Alert.alert("Error", "Could not save level.");
    } finally {
      setLoading(false);
    }
  };

  const LevelButton = ({ level, title, desc }: { level: string, title: string, desc: string }) => (
    <TouchableOpacity 
      style={styles.card} 
      onPress={() => setLevel(level)}
      disabled={loading}
    >
      <Text style={styles.cardTitle}>{title}</Text>
      <Text style={styles.cardDesc}>{desc}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.header}>Velg Nivå</Text>
        <Text style={styles.subHeader}>Choose your proficiency to help Rod adapt to you.</Text>

        {loading ? (
          <ActivityIndicator size="large" color="#007AFF" style={{marginTop: 50}} />
        ) : (
          <View style={styles.options}>
            <LevelButton 
              level="A1" 
              title="🐣 Nybegynner (A1)" 
              desc="I am just starting. Speak simple English/Norwegian mix." 
            />
            <LevelButton 
              level="A2" 
              title="🌱 Litt Øvet (A2)" 
              desc="I know the basics. Speak simple Norwegian." 
            />
            <LevelButton 
              level="B1" 
              title="🔥 Viderekommen (B1+)" 
              desc="I can hold a conversation. Speak naturally!" 
            />
          </View>
        )}

        <TouchableOpacity style={styles.testBtn} onPress={() => alert("Placement test coming soon!")}>
            <Text style={styles.testBtnText}>Or take a quick test to find out!</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7' },
  content: { padding: 20, flex: 1, justifyContent: 'center' },
  header: { fontSize: 32, fontWeight: 'bold', textAlign: 'center', marginBottom: 10 },
  subHeader: { fontSize: 16, color: '#666', textAlign: 'center', marginBottom: 40 },
  options: { gap: 15 },
  card: { backgroundColor: 'white', padding: 20, borderRadius: 16, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, elevation: 2 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', color: '#007AFF', marginBottom: 5 },
  cardDesc: { fontSize: 14, color: '#444' },
  testBtn: { marginTop: 30, padding: 15 },
  testBtnText: { textAlign: 'center', color: '#007AFF', fontWeight: '600', textDecorationLine: 'underline' }
});