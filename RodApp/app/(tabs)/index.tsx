import React, { useEffect, useState } from 'react';
import { 
  View, Text, StyleSheet, TouchableOpacity, Image, 
  ScrollView, FlatList, ActivityIndicator, Linking 
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ENDPOINTS } from '../../constants/config';
import { getOrCreateUserId } from '../../utils/user_manager';

interface Article {
  title: string;
  image_url: string;
  link: string;
  level: string;
  summary: string;
}

export default function HomeScreen() {
  const router = useRouter();
  const [news, setNews] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  // Check New User & Fetch News
  useEffect(() => {
    const init = async () => {
      // 1. Check Onboarding
      const { isNew } = await getOrCreateUserId();
      if (isNew) {
        setTimeout(() => router.push('/level_select' as any), 500);
      }

      // 2. Fetch News
      try {
        const res = await fetch(ENDPOINTS.MEDIA_NEWS);
        const data = await res.json();
        setNews(data.articles || []);
      } catch (e) {
        console.error("Failed to load news", e);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const renderNewsItem = ({ item }: { item: Article }) => (
    <TouchableOpacity 
      style={styles.card} 
      onPress={() => router.push('/media')} // Go to full Media Hub
    >
      <Image source={{ uri: item.image_url }} style={styles.cardImage} />
      <View style={styles.cardOverlay}>
        <View style={styles.levelBadge}>
            <Text style={styles.levelText}>{item.level}</Text>
        </View>
        <Text style={styles.cardTitle} numberOfLines={2}>{item.title}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        
        {/* 1. Header Section */}
        <View style={styles.headerSection}>
            <Text style={styles.greeting}>Hei! 👋</Text>
            <Text style={styles.subGreeting}>Klar for å lære norsk?</Text>
        </View>

        {/* 2. Chat Button */}
        <TouchableOpacity 
            style={styles.chatButton} 
            onPress={() => router.push('/chat')}
        >
            <Image 
                source={require('../../assets/icons/chat_icon.png')} 
                style={styles.chatBtnIcon} 
            />
            <Text style={styles.chatBtnText}>Chat med din AI-partner</Text>
        </TouchableOpacity>

        {/* 3. Media Carousel */}
        <View style={styles.mediaSection}>
            <View style={styles.sectionHeader}>
                <Text style={styles.sectionTitle}>Media Hub - Siste Nytt</Text>
                <TouchableOpacity onPress={() => router.push('/media')}>
                    <Text style={styles.seeAll}>Se alle</Text>
                </TouchableOpacity>
            </View>
            
            {loading ? (
                <ActivityIndicator color="#007AFF" style={{marginTop: 20}} />
            ) : (
                <FlatList
                    horizontal
                    data={news}
                    renderItem={renderNewsItem}
                    keyExtractor={(item) => item.link}
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.carouselContent}
                />
            )}
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F9FA' },
  scrollContent: { paddingBottom: 40 },
  
  // Header
  headerSection: { padding: 25 },
  greeting: { fontSize: 32, fontWeight: 'bold', color: '#333' },
  subGreeting: { fontSize: 18, color: '#666', marginTop: 5 },

  // Chat Button
  chatButton: {
    backgroundColor: '#007AFF',
    marginHorizontal: 20,
    height: 120,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
    marginBottom: 40,
  },
  chatBtnIcon: { width: 40, height: 40, tintColor: 'white', marginBottom: 10 },
  chatBtnText: { color: 'white', fontSize: 20, fontWeight: 'bold' },

  // Media Section
  mediaSection: { },
  sectionHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    paddingHorizontal: 25,
    marginBottom: 15 
  },
  sectionTitle: { fontSize: 20, fontWeight: 'bold', color: '#333' },
  seeAll: { color: '#007AFF', fontSize: 16 },

  // Carousel
  carouselContent: { paddingLeft: 25, paddingRight: 10, paddingBottom: 0 },
  card: {
    width: 200,
    height: 250,
    backgroundColor: 'white',
    borderRadius: 16,
    marginRight: 15,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },
  cardImage: { width: '100%', height: '100%' },
  cardOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.6)', // Dark gradient effect
    padding: 12,
    paddingTop: 30, // Space for gradient
  },
  cardTitle: { color: 'white', fontWeight: 'bold', fontSize: 14 },
  levelBadge: {
      position: 'absolute',
      top: -140, // Push it to top right of card
      right: 10,
      backgroundColor: 'white',
      paddingHorizontal: 8,
      paddingVertical: 10,
      borderRadius: 8,
  },
  levelText: { fontWeight: 'bold', fontSize: 12, color: '#007AFF' }
});