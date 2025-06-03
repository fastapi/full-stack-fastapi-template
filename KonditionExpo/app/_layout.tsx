// app/_layout.tsx

import React, { useEffect, useRef, useState } from "react";
import { Platform, Alert } from "react-native";

import { DarkTheme, DefaultTheme, ThemeProvider } from "@react-navigation/native";
import { useFonts } from "expo-font";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import "react-native-reanimated";

import { useColorScheme } from "@/hooks/useColorScheme";
import { UserProvider } from "@/contexts/UserContext";
import { WorkoutProvider } from "@/contexts/WorkoutContext";

// ─── IMPORTS FOR PUSH NOTIFICATIONS ─────────────────────────────────────────────
import * as Device from "expo-device";
import * as Notifications from "expo-notifications";
// ────────────────────────────────────────────────────────────────────────────────

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require("../assets/fonts/SpaceMono-Regular.ttf"),
  });

  // ─── STATE / REFS FOR PUSH REGISTRATION ────────────────────────────────────────
  const [expoPushToken, setExpoPushToken] = useState<string>("");
  const notificationListener = useRef<any>();
  const responseListener = useRef<any>();

  // Replace this with your actual user‐ID retrieval logic (e.g. from AuthContext)
  const fakeUserId = "user123";
  // ───────────────────────────────────────────────────────────────────────────────

  useEffect(() => {
    // 1) Configure how notifications are handled when the app is foregrounded:
    Notifications.setNotificationHandler({
      handleNotification: async (): Promise<Notifications.NotificationBehavior> => ({
        shouldShowAlert: true,      // (still allowed, but deprecated)
        shouldShowBanner: true,     // required on iOS 14+ to actually display in‐app banners
        shouldShowList: true,       // required on iOS 14+ to show in Notification Center
        shouldPlaySound: true,
        shouldSetBadge: false,
      }),
    });

    // 2) Register for push notifications & get Expo Push Token
    (async () => {
      if (!Device.isDevice) {
        Alert.alert("Push notifications require a physical device.");
        return;
      }

      // 2a) Check existing permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      if (existingStatus !== "granted") {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== "granted") {
        Alert.alert("Failed to get push token for push notifications!");
        return;
      }

      // 2b) Get the Expo Push Token
      const tokenData = await Notifications.getExpoPushTokenAsync();
      const token = tokenData.data;
      console.log("Obtained Expo Push Token:", token);
      setExpoPushToken(token);

      // 2c) Send that token to your FastAPI backend
      try {
        await fetch("http://localhost:8000/api/v1/notifications/register_push_token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: fakeUserId,
            expo_token: token,
          }),
        });
      } catch (err) {
        console.error("Error sending push token to backend:", err);
      }

      // 2d) (Android only) Create a notification channel
      if (Platform.OS === "android") {
        await Notifications.setNotificationChannelAsync("default", {
          name: "default",
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: "#FF231F7C",
        });
      }
    })();

    // 3) Foreground‐notification listener
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log("Notification Received (foreground):", notification);
      }
    );

    // 4) User‐tap listener (background or foreground)
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log("User tapped on notification:", response);
        // You can navigate or handle notification.data here
      }
    );

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
      if (responseListener.current) {
        Notifications.removeNotificationSubscription(responseListener.current);
      }
    };
  }, []);

  if (!loaded) {
    return null;
  }

  return (
    <AuthProvider>
      <UserProvider>
        <WorkoutProvider>
          <ThemeProvider value={colorScheme === "dark" ? DarkTheme : DefaultTheme}>
            <ProtectedRoute>
              <Stack>
                <Stack.Screen name="index" options={{ headerShown: false }} />
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="login" options={{ headerShown: false }} />
                <Stack.Screen name="signup" options={{ headerShown: false }} />
                <Stack.Screen name="signup2" options={{ headerShown: false }} />
                <Stack.Screen name="workout" options={{ headerShown: false }} />
                <Stack.Screen name="notification" options={{ headerShown: false }} />
                <Stack.Screen name="profile" options={{ headerShown: false }} />
                <Stack.Screen name="+not-found" />
              </Stack>
            </ProtectedRoute>
            <StatusBar style="auto" />
          </ThemeProvider>
        </WorkoutProvider>
      </UserProvider>
    </AuthProvider>
  );
}
