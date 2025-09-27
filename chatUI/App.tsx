// App.tsx
import React, { useState, useRef } from "react";
import { StyleSheet, Text, View, FlatList, TouchableOpacity, ActivityIndicator, SafeAreaView, Alert } from "react-native";
import { Audio } from "expo-av";
import axios from "axios";
import { Ionicons } from "@expo/vector-icons";

type Message = {
  id: string;
  text: string;
  sender: "user" | "assoral";
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [loading, setLoading] = useState(false);
  const soundRef = useRef<Audio.Sound | null>(null);
  const BASE_URL = "http://192.168.1.172:8000";   // testing on my local server

  const recordingOptions: Audio.RecordingOptions = {
    android: { extension: ".wav", outputFormat: 2, audioEncoder: 3, sampleRate: 16000, numberOfChannels: 1, bitRate: 128000 },
    ios: { extension: ".wav", audioQuality: 2, sampleRate: 16000, numberOfChannels: 1, bitRate: 128000, linearPCMBitDepth: 16, linearPCMIsBigEndian: false, linearPCMIsFloat: false },
    web: { mimeType: "audio/wav", bitsPerSecond: 128000 },
  };

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission required", "Microphone access is needed.");
        return;
      }
      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });
      const newRecording = new Audio.Recording();
      await newRecording.prepareToRecordAsync(recordingOptions);
      await newRecording.startAsync();
      setRecording(newRecording);
    } catch (err) {
      console.error("Failed to start recording:", err);
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    setLoading(true);
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);

      if (uri) {
        const formData = new FormData();
        formData.append("file", { uri, name: "audio.wav", type: "audio/wav" } as any);

        const transcribeRes = await axios.post(`${BASE_URL}/transcrive`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const userText = transcribeRes.data.transcript;
        const userMessage: Message = { id: Date.now().toString(), text: userText, sender: "user" };
        setMessages(prev => [...prev, userMessage]);

        const askRes = await axios.post(`${BASE_URL}/ask`, { text: userText });
        const assoralText = askRes.data.response;
        const assoralMessage: Message = { id: (Date.now() + 1).toString(), text: assoralText, sender: "assoral" };
        setMessages(prev => [...prev, assoralMessage]);

        if (askRes.data.audio_file) {
          const { sound } = await Audio.Sound.createAsync({ uri: askRes.data.audio_file });
          soundRef.current = sound;
          await sound.playAsync();
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const stopConversation = async () => {
    if (recording) {
      await recording.stopAndUnloadAsync();
      setRecording(null);
    }
    if (soundRef.current) {
      await soundRef.current.stopAsync();
      await soundRef.current.unloadAsync();
      soundRef.current = null;
    }
    setMessages([]);
    setLoading(false);
    Alert.alert("Conversation stopped");
  };

  const renderItem = ({ item }: { item: Message }) => (
    <View style={[styles.bubble, item.sender === "user" ? styles.userBubble : styles.assoralBubble]}>
      <Text style={{ color: item.sender === "user" ? "#000" : "#000"}}>{item.text}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Messages */}
      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={{ padding: 10, paddingBottom: 150, paddingTop: 50}}
      />

      {loading && <ActivityIndicator size="large" color="#35363F" style={styles.loading} />}

      {/* Mic Button with Long Press to Stop Conversation */}
      <TouchableOpacity
        style={[styles.micButton, recording ? { backgroundColor: "red" } : {}]}
        onPress={recording ? stopRecording : startRecording}
        onLongPress={stopConversation}
      >
        <Ionicons name="mic" size={36} color="#fff" />
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "white" }, 
  topBar: {
    width: "100%",
    height: 60,
    backgroundColor: "#1B5B7E",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-end",
    paddingHorizontal: 15,
  },
  topBarButton: {
    backgroundColor: "#9BC0DA",
    paddingHorizontal: 18,
    paddingVertical: 5,
    borderRadius: 10,
    position: "absolute",
    right: 15,
    top: 27,
  },
  topBarButtonText: {
    color: "#1B5B7E",
    fontWeight: "bold",
    textAlign: "center",
  },
  micButton: {
    position: "absolute",
    bottom: 50,
    alignSelf: "center",
    backgroundColor: "#f6c9d5ff",
    width: 70,
    height: 70,
    borderRadius: 35,
    justifyContent: "center",
    alignItems: "center",
  },
  bubble: {
    padding: 10,
    borderRadius: 10,
    marginVertical: 5,
    maxWidth: "80%",
  },
  userBubble: { backgroundColor: "#f6c9d5ff", alignSelf: "flex-end" },
  assoralBubble: { backgroundColor: "#e6e6e6", alignSelf: "flex-start" },
  userText: { color: "#1B5B7E" },      
  assoralText: { color: "#CCE1EF" },    
  loading: { position: "absolute", bottom: 130, alignSelf: "center" },
});



