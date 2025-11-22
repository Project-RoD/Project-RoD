import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';
import { Platform } from 'react-native';

const USER_ID_KEY = 'rod_user_id_v1';;

// Helper to get ID
export async function getOrCreateUserId(): Promise<{ id: string, isNew: boolean }> {
  try {
    // 1. Web Support 
    if (Platform.OS === 'web') {
      let webId = localStorage.getItem(USER_ID_KEY);
      if (!webId) {
        webId = Crypto.randomUUID();
        localStorage.setItem(USER_ID_KEY, webId);
        return { id: webId, isNew: true }; 
      }
      return { id: webId, isNew: false };
    }

    // 2. Native Support
    let userId = await SecureStore.getItemAsync(USER_ID_KEY);

    if (!userId) {
      userId = Crypto.randomUUID();
      await SecureStore.setItemAsync(USER_ID_KEY, userId);
      console.log('🆕 Generated New Identity:', userId);
      return { id: userId, isNew: true }; 
    } 
    
    console.log('👤 Recognized Returning User:', userId);
    return { id: userId, isNew: false };

  } catch (error) {
    
    return { id: 'fallback', isNew: false };
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