import React from 'react';
import { Tabs, useRouter } from 'expo-router';
import { Image, StyleSheet, Text, View, TouchableOpacity } from 'react-native';


// Helper Components for the Header
function StreakCounter() {
  const streak = 0; // Placeholder
  return (
    <View style={styles.headerLeftContainer}>
      <Image
        source={require('../../assets/icons/fire_icon.png')}
        style={styles.headerIcon}
      />
      <Text style={styles.headerText}>{streak} Days</Text>
    </View>
  );
}

function MenuButton() {
  return (
    <View style={styles.headerLeftContainer}>
      <TouchableOpacity onPress={() => console.log('Menu pressed!')}>
        <Image
          source={require('../../assets/icons/menu_icon.png')}
          style={[styles.headerIcon, { tintColor: 'black' }]}
        />
      </TouchableOpacity>
    </View>
  );
}

function ProfileIcon() {
  const router = useRouter();
  return (
    <View style={styles.headerRightContainer}>
      <TouchableOpacity onPress={() => router.push('/profile')}>
        <Image
          source={require('../../assets/icons/profile_icon.png')}
          style={styles.profileIcon}
        />
      </TouchableOpacity>
    </View>
  );
}

// TabBarIcon component
function TabBarIcon({ path, color }: { path: any; color: string }) {
  return (
    <Image
      source={path}
      style={[styles.tabIcon, { tintColor: color }]}
    />
  );
}

// The Main Layout
export default function TabLayout() {
  return (
    <Tabs
      initialRouteName="index" // Starts on Home
      screenOptions={{
        headerShown: true,
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'black', // Inactive tabs are black

        // Tab bar styles
        tabBarStyle: {
          height: 90,
          paddingTop: 5,
          paddingBottom: 30,
          paddingLeft: 4,
        },
        tabBarLabelStyle: {
          fontSize: 12,
        },
      }}
    >
      <Tabs.Screen
        name="chat"
        options={{
          title: 'RoD Chat',
          headerLeft: () => <MenuButton />,
          headerRight: () => <ProfileIcon />,

          // Centering Layout
          headerLeftContainerStyle: {
            flexBasis: 110,
            justifyContent: 'flex-start',
          },
          headerRightContainerStyle: {
            flexBasis: 110,
            justifyContent: 'flex-end',
          },
          headerTitleContainerStyle: {
            flex: 20,
            alignItems: 'center',
          },
          headerTitleStyle: {
            transform: [{ translateX: 0 }],
          },

          tabBarLabel: 'Chat',
          tabBarIcon: ({ color }) => (
            <TabBarIcon
              path={require('../../assets/icons/chat_icon.png')}
              color={color}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="index"
        options={{
          title: '',

          headerLeft: () => <StreakCounter />,
          headerRight: () => <ProfileIcon />,

          // Centering Layout
          headerLeftContainerStyle: {
            flexBasis: 110,
            justifyContent: 'flex-start',
          },
          headerRightContainerStyle: {
            flexBasis: 110,
            justifyContent: 'flex-end',
          },
          headerTitleContainerStyle: {
            flex: 1,
            alignItems: 'center',
          },

          tabBarLabel: 'Home',
          tabBarIcon: ({ color }) => (
            <TabBarIcon
              path={require('../../assets/icons/home_icon.png')}
              color={color}
            />
          ),
        }}
      />
      <Tabs.Screen
        name="games"
        options={{
          title: 'Game Hub',
          headerLeft: () => <StreakCounter />,
          headerRight: () => <ProfileIcon />,

          // Centering Layout
          headerLeftContainerStyle: {
            flexBasis: 110,
            justifyContent: 'flex-start',
          },
          headerRightContainerStyle: {
            flexBasis: 110,
            justifyContent: 'flex-end',
          },
          headerTitleContainerStyle: {
            flex: 15,
            alignItems: 'center',
          },
          headerTitleStyle: {
            transform: [{ translateX: 0 }],
          },

          tabBarLabel: 'Games',
          tabBarIcon: ({ color }) => (
            <TabBarIcon
              path={require('../../assets/icons/game_icon.png')}
              color={color}
            />
          ),
        }}
      />
    </Tabs>
  );
}

// Styles for ALL icons
const styles = StyleSheet.create({
  tabIcon: {
    width: 28,
    height: 28,
  },
  headerLeftContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: 15,
    marginBottom: 3,
  },
  headerRightContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginRight: 15,
  },
  headerIcon: {
    width: 32,
    height: 32,
  },
  headerText: {
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 5,
    marginTop: 5,
  },
  profileIcon: {
    width: 30,
    height: 30,
    tintColor: 'black',
  },
});