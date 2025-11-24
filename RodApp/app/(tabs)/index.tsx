import React, { useEffect } from 'react';
import { View, Button, StyleSheet, Image, Text, TouchableOpacity } from 'react-native';
import { Link, useRouter } from 'expo-router';
import { getOrCreateUserId } from '../../utils/user_manager';

export default function HomeScreen() {
  const router = useRouter();

  // Check for New User on App Launch
  useEffect(() => {
    const checkUser = async () => {
      const { isNew } = await getOrCreateUserId();
      
      if (isNew) {
        // Give the UI a split second to load, then pop the modal
        setTimeout(() => {
          router.push('/level_select' as any);
        }, 500);
      }
    };
    checkUser();
  }, []);

  return (
    <View style={styles.container}>
      
      {/* Simple Logo or Welcome Text */}
      <View style={styles.welcomeContainer}>
        <Text style={styles.welcomeText}>Welcome to RoD</Text>
        <Text style={styles.subText}>Your AI Language Companion</Text>
      </View>

      {/* Navigation Buttons */}
      <View style={styles.buttonContainer}>
        <Link href="/chat" asChild>
          <Button title="Start Chatting" />
        </Link>

        <Link href="/media" asChild>
           <Button title="Media Hub" />
        </Link>
        
        <Link href="/games" asChild>
           <Button title="Game Hub" />
        </Link>
      </View>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'white',
  },
  welcomeContainer: {
    marginBottom: 50,
    alignItems: 'center',
  },
  welcomeText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  subText: {
    fontSize: 16,
    color: '#888',
    marginTop: 5,
  },
  buttonContainer: {
    gap: 20,
    width: '80%',
  },
});