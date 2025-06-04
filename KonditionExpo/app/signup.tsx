import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { router } from 'expo-router';
import { useUser } from '@/contexts/UserContext';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_URL } from "@/constants/config";





export default function SignUpScreen() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const { setName: setUserName } = useUser();

  const handleCreateAccount = async () => {
    if (password !== confirmPassword) {
      alert("Passwords don't match");
      return;
    }
  
    try {
      const res = await fetch(`http://localhost:8000/api/v1/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name }),
      });
      console.log("response from signup: ", res);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        console.log("ERROR DATA: ", errData);
        const errMsg =
          errData.detail || JSON.stringify(errData) || res.statusText || "Unknown error";
        alert("Signup failed: " + errMsg);
        return;
      }      
      const data = await res.json();
      console.log("JSON DATA OF SIGNUP: ", data)
      if (res.ok) {
        // Optionally, auto-login after signup
        if (data.access_token) {
          await AsyncStorage.setItem("access_token", data.access_token);
        } else {
          console.warn("No token returned from signup");
        }
        setUserName(name);
        router.replace('/signup2');
      } else {
        alert(data.detail || "Signup failed");
      }
    } catch (err) {
      console.error("Signup error", err);
      alert("Something went wrong during signup.");
    }
  };
  

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Create Your Account</Text>

      <Input label="Full Name" value={name} onChangeText={setName} />
      <Input label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
      <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry />
      <Input label="Confirm Password" value={confirmPassword} onChangeText={setConfirmPassword} secureTextEntry />

      <Button title="Sign Up" onPress={handleCreateAccount} fullWidth />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, flexGrow: 1, justifyContent: 'center' },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 24, textAlign: 'center' },
});
