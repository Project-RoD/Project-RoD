import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { ENDPOINTS } from '../constants/config';
import { getOrCreateUserId } from '../utils/user_manager';

export default function ProfileScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const changeLevel = async (newLevel: string) => {
    setLoading(true);
    try {
      const { id } = await getOrCreateUserId();
      await fetch(ENDPOINTS.USER_LEVEL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: id, level: newLevel }),
      });
      Alert.alert("Success", `Level changed to ${newLevel}`);
    } catch (e) {
      Alert.alert("Error", "Could not update level.");
    } finally {
      setLoading(false);
    }
  };

  const LevelOption = ({ level, label }: { level: string, label: string }) => (
    <TouchableOpacity 
      style={styles.option} 
      onPress={() => changeLevel(level)}
      disabled={loading}
    >
      <Text style={styles.optionText}>{label}</Text>
      {loading && <ActivityIndicator size="small" color="#007AFF" />}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={styles.doneBtn}>Done</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Proficiency Level</Text>
        <LevelOption level="A1" label="🐣 Nybegynner (A1)" />
        <LevelOption level="A2" label="🌱 Litt Øvet (A2)" />
        <LevelOption level="B1" label="🔥 Viderekommen (B1+)" />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App Info</Text>
        <Text style={styles.infoText}>Rod Beta v0.7</Text>
        <Text style={styles.infoText}>User ID: {Math.random().toString(36).slice(-6)}...</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, backgroundColor: 'white' },
  title: { fontSize: 24, fontWeight: 'bold' },
  doneBtn: { fontSize: 16, color: '#007AFF', fontWeight: '600' },
  section: { marginTop: 30, paddingHorizontal: 20 },
  sectionTitle: { fontSize: 14, color: '#666', marginBottom: 10, textTransform: 'uppercase' },
  option: { backgroundColor: 'white', padding: 15, borderRadius: 10, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between' },
  optionText: { fontSize: 16, fontWeight: '500' },
  infoText: { color: '#888', marginBottom: 5 }
});