import React, { useEffect, useState } from 'react';
import { 
  View, Text, StyleSheet, FlatList, Image, TouchableOpacity, 
  ActivityIndicator, Linking, Alert 
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { ENDPOINTS } from '../constants/config';

interface Article {
  title: string;
  summary: string;
  image_url: string;
  link: string;
  level: string;
}

const CATEGORIES = ["Nyheter", "Video", "Musikk", "Bøker"];

export default function MediaScreen() {
  const router = useRouter();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("Nyheter");
  
  // FILTER STATE
  const [filterLevel, setFilterLevel] = useState<string | null>(null);

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      const res = await fetch(ENDPOINTS.MEDIA_NEWS);
      const data = await res.json();
      setArticles(data.articles || []);
    } catch (e) {
      console.error("Failed to load media", e);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenLink = (url: string) => {
    Linking.openURL(url).catch(() => Alert.alert("Error", "Could not open link"));
  };

  const handleDiscuss = (item: Article) => {
    const contextPayload = JSON.stringify({
        title: item.title,
        summary: item.summary
    });

    router.dismiss();
    router.push({ 
        pathname: '/(tabs)/chat', 
        params: { 
            conversationId: 'new', 
            mediaContext: contextPayload 
        } 
    });
  };

  // FILTER LOGIC
  const filteredArticles = articles.filter(article => {
     if (!filterLevel) return true; 
     return article.level === filterLevel;
  });

  const renderItem = ({ item }: { item: Article }) => (
    <View style={styles.card}>
      <Image source={{ uri: item.image_url }} style={styles.cardImage} />
      
      <View style={styles.cardContent}>
        <View style={styles.metaRow}>
            <View style={styles.badge}>
                <Text style={styles.badgeText}>{item.level}</Text>
            </View>
            <Text style={styles.source}>NRK.no</Text>
        </View>

        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.summary} numberOfLines={3}>{item.summary}</Text>

        <View style={styles.actionRow}>
            <TouchableOpacity 
                style={[styles.btn, styles.readBtn]} 
                onPress={() => handleOpenLink(item.link)}
            >
                <Text style={styles.readText}>Les Saken</Text>
            </TouchableOpacity>

            <TouchableOpacity 
                style={[styles.btn, styles.discussBtn]} 
                onPress={() => handleDiscuss(item)}
            >
                <Image source={require('../assets/icons/chat_icon.png')} style={styles.btnIcon} />
                <Text style={styles.discussText}>Diskuter</Text>
            </TouchableOpacity>
        </View>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Media Hub</Text>
        <TouchableOpacity onPress={() => router.back()}>
            <Text style={styles.closeText}>Lukk</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.tabs}>
        {CATEGORIES.map((cat) => (
            <TouchableOpacity 
                key={cat} 
                style={[styles.tabItem, activeTab === cat && styles.tabActive]}
                onPress={() => setActiveTab(cat)}
            >
                <Text style={[styles.tabText, activeTab === cat && styles.tabTextActive]}>{cat}</Text>
            </TouchableOpacity>
        ))}
      </View>

      {loading ? (
          <ActivityIndicator size="large" color="#007AFF" style={{marginTop: 50}} />
      ) : activeTab === "Nyheter" ? (
          <FlatList
            data={filteredArticles}
            renderItem={renderItem}
            keyExtractor={(item) => item.link}
            contentContainerStyle={{ padding: 15, paddingBottom: 40 }}
            ListHeaderComponent={
                <View style={styles.filterRow}>
                    <TouchableOpacity 
                        style={[styles.filterBtn, !filterLevel && styles.filterActive]} 
                        onPress={() => setFilterLevel(null)}
                    >
                        <Text style={!filterLevel ? styles.textActive : styles.textInactive}>Alle</Text>
                    </TouchableOpacity>
                    
                    {['A2', 'B1', 'B2', 'C1'].map(level => (
                        <TouchableOpacity 
                            key={level}
                            style={[styles.filterBtn, filterLevel === level && styles.filterActive]} 
                            onPress={() => setFilterLevel(level)}
                        >
                            <Text style={filterLevel === level ? styles.textActive : styles.textInactive}>{level}</Text>
                        </TouchableOpacity>
                    ))}
                </View>
            }
          />
      ) : (
          <View style={styles.emptyState}>
              <Text style={styles.emptyText}>Kommer Snart / Coming Soon</Text>
          </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, backgroundColor: 'white' },
  headerTitle: { fontSize: 24, fontWeight: 'bold' },
  closeText: { color: '#007AFF', fontSize: 16, fontWeight: '600' },
  tabs: { flexDirection: 'row', padding: 15, gap: 10 },
  tabItem: { paddingVertical: 8, paddingHorizontal: 16, borderRadius: 20, backgroundColor: '#E5E5EA' },
  tabActive: { backgroundColor: '#007AFF' },
  tabText: { color: '#666', fontWeight: '600' },
  tabTextActive: { color: 'white' },
  card: { backgroundColor: 'white', borderRadius: 16, marginBottom: 20, overflow: 'hidden', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, elevation: 2 },
  cardImage: { width: '100%', height: 180 },
  cardContent: { padding: 15 },
  metaRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  badge: { backgroundColor: '#E1F5FE', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4 },
  badgeText: { color: '#0288D1', fontWeight: 'bold', fontSize: 12 },
  source: { color: '#888', fontSize: 12 },
  title: { fontSize: 18, fontWeight: 'bold', marginBottom: 8 },
  summary: { fontSize: 14, color: '#555', lineHeight: 20, marginBottom: 15 },
  actionRow: { flexDirection: 'row', gap: 10 },
  btn: { flex: 1, padding: 12, borderRadius: 10, alignItems: 'center', justifyContent: 'center', flexDirection: 'row' },
  readBtn: { backgroundColor: '#F2F2F7' },
  readText: { color: '#007AFF', fontWeight: '600' },
  discussBtn: { backgroundColor: '#007AFF' },
  discussText: { color: 'white', fontWeight: 'bold', marginLeft: 5 },
  btnIcon: { width: 16, height: 16, tintColor: 'white' },
  emptyState: { alignItems: 'center', marginTop: 50 },
  emptyText: { color: '#888', fontSize: 16 },
  // Filter Styles
  filterRow: { flexDirection: 'row', marginBottom: 15, gap: 10 },
  filterBtn: { paddingVertical: 6, paddingHorizontal: 12, borderRadius: 15, backgroundColor: 'white', borderWidth: 1, borderColor: '#DDD' },
  filterActive: { backgroundColor: '#007AFF', borderColor: '#007AFF' },
  textActive: { color: 'white', fontWeight: 'bold', fontSize: 12 },
  textInactive: { color: '#666', fontSize: 12 },
});