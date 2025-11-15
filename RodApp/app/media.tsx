import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function MediaScreen() {
  return (
    <View style={styles.container}>
      <Text>Media Hub (Coming Soon!)</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center' },
});