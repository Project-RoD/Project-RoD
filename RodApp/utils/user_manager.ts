import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';
import { Platform } from 'react-native';

const USER_ID_KEY = 'rod_user_id_v1';

// Helper to get ID
export async function getOrCreateUserId(): Promise<string> {
  try {
    // 1. Web Support (SecureStore doesn't work on Web, so we use localStorage)
    if (Platform.OS === 'web') {
      let webId = localStorage.getItem(USER_ID_KEY);
      if (!webId) {
        webId = Crypto.randomUUID();
        localStorage.setItem(USER_ID_KEY, webId);
      }
      return webId;
    }

    // 2. Native Support (iOS/Android)
    let userId = await SecureStore.getItemAsync(USER_ID_KEY);

    if (!userId) {
      // No ID found? Create one and save it forever.
      userId = Crypto.randomUUID();
      await SecureStore.setItemAsync(USER_ID_KEY, userId);
      console.log('🆕 Generated New Identity:', userId);
    } else {
      console.log('👤 Recognized Returning User:', userId);
    }

    return userId;
  } catch (error) {
    console.error('Error retrieving User ID:', error);
    // Emergency fallback to prevent crash
    return 'guest-fallback-' + Math.random().toString(36).substring(7);
  }
}

// Helper to clear ID (for "Logout" button later)
export async function clearUserId() {
  if (Platform.OS === 'web') {
    localStorage.removeItem(USER_ID_KEY);
  } else {
    await SecureStore.deleteItemAsync(USER_ID_KEY);
  }
}