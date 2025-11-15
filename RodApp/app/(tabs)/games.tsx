import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function GamesScreen() {
  return (
    <View style={styles.container}>
      <Text>Game Hub (Coming Soon!)</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});