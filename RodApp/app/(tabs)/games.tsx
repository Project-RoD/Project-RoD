import React, { useState, useEffect } from 'react';
import { 
  View, Text, StyleSheet, TouchableOpacity, Alert 
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { getRandomWord, isWordValid } from '../../constants/word_list';

const MAX_GUESSES = 6;
const WORD_LENGTH = 5;

export default function GameScreen() {
  const [solution, setSolution] = useState("");
  const [guesses, setGuesses] = useState<string[]>([]);
  const [currentGuess, setCurrentGuess] = useState("");
  const [gameStatus, setGameStatus] = useState<'playing' | 'won' | 'lost'>('playing');

  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = () => {
    setSolution(getRandomWord());
    setGuesses([]);
    setCurrentGuess("");
    setGameStatus('playing');
  };

  const handleKeyPress = (key: string) => {
    if (gameStatus !== 'playing') return;

    if (key === 'ENTER') {
      submitGuess();
    } else if (key === '⌫') {
      setCurrentGuess(prev => prev.slice(0, -1));
    } else {
      if (currentGuess.length < WORD_LENGTH) {
        setCurrentGuess(prev => prev + key);
      }
    }
  };

  const submitGuess = () => {
    if (currentGuess.length !== WORD_LENGTH) {
      Alert.alert("For kort", "Ordet må ha 5 bokstaver!");
      return;
    }

    const newGuesses = [...guesses, currentGuess];
    setGuesses(newGuesses);
    setCurrentGuess("");

    if (currentGuess === solution) {
      setGameStatus('won');
      Alert.alert("Gratulerer!", `Du klarte det! Ordet var ${solution}`, [
        { text: "Spill igjen", onPress: startNewGame }
      ]);
    } else if (newGuesses.length >= MAX_GUESSES) {
      setGameStatus('lost');
      Alert.alert("Beklager", `Du tapte. Ordet var ${solution}`, [
        { text: "Prøv igjen", onPress: startNewGame }
      ]);
    }
  };

  // RENDER HELPERS
  const getCellColor = (guess: string, index: number, char: string) => {
    if (char === solution[index]) return '#538D4E'; // Green
    if (solution.includes(char)) return '#B59F3B'; // Yellow
    return '#3A3A3C'; // Gray
  };

  const renderGrid = () => {
    const rows = [];
    for (let i = 0; i < MAX_GUESSES; i++) {
      const isCurrentRow = i === guesses.length;
      const guess = guesses[i] || "";
      const rowChars = [];

      for (let j = 0; j < WORD_LENGTH; j++) {
        const char = isCurrentRow ? currentGuess[j] : guess[j];
        let style: any = styles.cell; 
        let textStyle = styles.cellText;

        if (guess) {
           const bg = getCellColor(guess, j, char || "");
           style = { ...styles.cell, backgroundColor: bg, borderColor: bg };
           textStyle = { ...styles.cellText, color: 'white' };
        } else if (char) {
           style = { ...styles.cell, borderColor: '#888' };
        }

        rowChars.push(
          <View key={j} style={style}>
            <Text style={textStyle}>{char || ""}</Text>
          </View>
        );
      }
      rows.push(<View key={i} style={styles.row}>{rowChars}</View>);
    }
    return rows;
  };

  const KeyboardKey = ({ label, width = 30 }: { label: string, width?: number }) => (
    <TouchableOpacity 
        style={[styles.key, { width }]} 
        onPress={() => handleKeyPress(label)}
    >
      <Text style={styles.keyText}>{label}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.title}>ORDLE</Text>
      </View>
      
      <View style={styles.gridContainer}>
        {renderGrid()}
      </View>

      <View style={styles.keyboardContainer}>
        <View style={styles.keyboardRow}>
            {['Q','W','E','R','T','Y','U','I','O','P','Å'].map(k => <KeyboardKey key={k} label={k} />)}
        </View>
        <View style={styles.keyboardRow}>
            {['A','S','D','F','G','H','J','K','L','Ø','Æ'].map(k => <KeyboardKey key={k} label={k} />)}
        </View>
        <View style={styles.keyboardRow}>
            <KeyboardKey label="ENTER" width={48} /> 
            {['Z','X','C','V','B','N','M'].map(k => <KeyboardKey key={k} label={k} />)}
            <KeyboardKey label="⌫" width={40} />
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'white', alignItems: 'center' },
  header: { marginTop: 0, marginBottom: 30 },
  title: { fontSize: 32, fontWeight: 'bold', letterSpacing: 5, color: '#333' },
  
  gridContainer: { marginBottom: 30 },
  row: { flexDirection: 'row', marginBottom: 8, gap: 6 },
  cell: { 
    width: 50, height: 50, 
    borderWidth: 2, borderColor: '#E5E5EA', 
    justifyContent: 'center', alignItems: 'center',
    borderRadius: 4
  },
  cellText: { fontSize: 24, fontWeight: 'bold', color: 'black' },

  keyboardContainer: { alignItems: 'center', gap: 8 },
  keyboardRow: { flexDirection: 'row', gap: 3 },
  key: { 
    height: 50, backgroundColor: '#D3D6DA', 
    justifyContent: 'center', alignItems: 'center', 
    borderRadius: 4 
  },
  keyText: { fontWeight: 'bold', fontSize: 13 }
});