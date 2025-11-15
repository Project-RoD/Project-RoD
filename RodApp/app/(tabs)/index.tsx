import React from 'react';
import { View, Button, StyleSheet } from 'react-native';
import { Link } from 'expo-router'; // Use Link for navigation

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      
      {/* This Link will navigate to 'app/chat.tsx' */}
      <Link href="/chat" asChild>
        <Button title="Chat with RoD" />
      </Link>

      <Button title="Media Hub (Coming Soon)" disabled={true} />
      

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 20, // Adds space between buttons
  },
});