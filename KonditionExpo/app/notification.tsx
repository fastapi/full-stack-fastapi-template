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
} from "react-native";

// Define the shape of each quote, matching QuoteOut from the backend
type QuoteItem = {
  date: string; // "YYYY-MM-DD"
  text: string;
};

export default function NotificationScreen() {
  const [notifications, setNotifications] = useState<QuoteItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the last 7 days of quotes from the backend
    // Replace localhost with your actual host or LAN IP if testing on device
    fetch("http://localhost:8000/api/v1/notifications/quotes")
      .then((res) => res.json())
      .then((data: QuoteItem[]) => {
        // data is an array like [{ date: "2025-06-05", text: "..." }, …]
        setNotifications(data);
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
        <Text style={styles.headerTitle}>Daily Quotes</Text>
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

const { width, height } = Dimensions.get("window");

const styles = StyleSheet.create({
  container: {
    flex: 1,
    width,
    height,
    backgroundColor: "#ffffff",
    alignItems: "center",
    justifyContent: "center",
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
    backgroundColor: "#fafafa",
    alignItems: "center",
    width: "100%",
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: "bold",
  },
  listContent: {
    paddingVertical: 8,
    width: "100%",
  },
  item: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
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
