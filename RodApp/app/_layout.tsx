import { Stack, useRouter } from 'expo-router';
import { Image, TouchableOpacity, StyleSheet } from 'react-native';

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
    <Stack>
      <Stack.Screen 
        name="(tabs)" // This targets all tab screens
        options={{
          headerShown: false, 
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
        }}
      />
    </Stack>
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