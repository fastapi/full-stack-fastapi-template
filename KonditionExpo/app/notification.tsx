// app/screens/NotificationScreen.tsx

import React, { useState, useEffect } from "react";
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  FlatList,
  Dimensions,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import { useRouter } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

// Define the shape of each quote, matching QuoteOut from the backend
type QuoteItem = {
  date: string; // "YYYY-MM-DD"
  text: string;
};

export default function NotificationScreen() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<QuoteItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the last 7 days of quotes from the backend
    // Replace "localhost" with your LAN IP or actual host when testing on device
    fetch("http://localhost:8000/api/v1/notifications/quotes")
      .then((res) => res.json())
      .then((data: QuoteItem[]) => {
        setNotifications(data); // data is an array like [{ date: "2025-06-05", text: "..." }, …]
      })
      .catch((err) => {
        console.error("Error fetching quotes:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const renderItem = ({ item }: { item: QuoteItem }) => (
    <View style={styles.item}>
      <View style={styles.itemText}>
        <Text style={styles.title} numberOfLines={2}>
          {item.text}
        </Text>
        <Text style={styles.time}>{item.date}</Text>
      </View>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#333" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => {
            // Go back in the navigation stack (like HomeScreen’s notification button did)
            router.back();
          }}
        >
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Daily Quotes</Text>
        {/* Dummy view to balance centering (same width as backButton) */}
        <View style={styles.placeholder} />
      </View>

      <FlatList
        data={notifications}
        keyExtractor={(item) => item.date}
        renderItem={renderItem}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        contentContainerStyle={styles.listContent}
      />
    </SafeAreaView>
  );
}

const { width } = Dimensions.get("window");

const styles = StyleSheet.create({
  // ——— Container now matches HomeScreen’s container style ———
  container: {
    flex: 1,
    backgroundColor: "#FFFFFF",
  },

  // ——— Header is identical in structure to the back‐arrow version previously shown ———
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
    backgroundColor: "#fafafa",
    width: "100%",
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    flex: 1,
    textAlign: "center",
    fontSize: 20,
    fontWeight: "bold",
    color: "#333",
  },
  placeholder: {
    width: 32, // same width as backButton + icon, to keep title centered
  },

  // ——— Make the FlatList’s content match HomeScreen’s padding:16 ———
  listContent: {
    padding: 16,
    paddingBottom: 80, // if you want similar bottom padding (e.g., for any tab bar)
    width: "100%",
  },

  // ——— Each item in the quote list ———
  item: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderRadius: 8, // optional, just to match HomeScreen’s card feel
    marginBottom: 8,
  },
  itemText: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    color: "#333",
  },
  time: {
    fontSize: 12,
    color: "#888",
    marginTop: 4,
  },
  separator: {
    height: 1,
    backgroundColor: "#eee",
    marginLeft: 16,
    width: "100%",
  },
});
