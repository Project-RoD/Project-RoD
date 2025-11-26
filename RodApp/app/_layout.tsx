import { Stack, useRouter } from 'expo-router';
import { Image, TouchableOpacity, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';

function ProfileIcon() {
  const router = useRouter();
  return (
    <TouchableOpacity onPress={() => router.push('/profile')}>
      <Image 
        source={require('../assets/icons/profile_icon.png')}
        style={styles.profileIcon}
      />
    </TouchableOpacity>
  );
}

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack>
        <Stack.Screen 
          name="(tabs)" 
          options={{ headerShown: false }} 
        />
        <Stack.Screen
          name="level_select"
          options={{
            title: 'Select Level',
            presentation: 'modal',
            headerShown: false,
            gestureEnabled: false 
          }}
        />
        <Stack.Screen
          name="profile"
          options={{
            title: 'Profile',
            presentation: 'modal',
            headerRight: () => <ProfileIcon />,
          }}
        />
        <Stack.Screen
          name="history"
          options={{
            title: 'History',
            presentation: 'modal',
            headerShown: false,
          }}
        />
        <Stack.Screen
          name="media" 
          options={{
            title: 'Media Hub',
            presentation: 'modal',
            headerShown: false,
          }}
        />
      </Stack>
    </>
  );
}

const styles = StyleSheet.create({
  profileIcon: {
    width: 30,
    height: 30,
    marginRight: 1,
    tintColor: 'gray',
  }
});