import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, TextInput } from 'react-native';
import { getApiBaseUrl, setCustomApiUrl, getNetworkSetupInstructions } from '../config/api';

interface DevToolsProps {
  visible: boolean;
  onClose: () => void;
}

export const DevTools: React.FC<DevToolsProps> = ({ visible, onClose }) => {
  const [customUrl, setCustomUrl] = useState('');
  const currentUrl = getApiBaseUrl();
  const instructions = getNetworkSetupInstructions();

  if (!visible) return null;

  const handleSetCustomUrl = () => {
    if (customUrl.trim()) {
      setCustomApiUrl(customUrl.trim());
      Alert.alert('Success', `API URL updated to: ${customUrl.trim()}`);
      setCustomUrl('');
    }
  };

  const showInstructions = () => {
    Alert.alert(
      instructions.title,
      instructions.instructions.join('\n'),
      [{ text: 'OK' }]
    );
  };

  const testConnection = async () => {
    try {
      const response = await fetch(`${currentUrl}/docs`);
      if (response.ok) {
        Alert.alert('Success', 'API connection successful!');
      } else {
        Alert.alert('Error', `API returned status: ${response.status}`);
      }
    } catch (error) {
      Alert.alert('Error', `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <View style={styles.overlay}>
      <View style={styles.container}>
        <ScrollView style={styles.content}>
          <Text style={styles.title}>Development Tools</Text>
          
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Current API URL</Text>
            <Text style={styles.urlText}>{currentUrl}</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Test Connection</Text>
            <TouchableOpacity style={styles.button} onPress={testConnection}>
              <Text style={styles.buttonText}>Test API Connection</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Custom API URL</Text>
            <TextInput
              style={styles.input}
              value={customUrl}
              onChangeText={setCustomUrl}
              placeholder="http://192.168.1.100:8000/api/v1"
              placeholderTextColor="#999"
            />
            <TouchableOpacity style={styles.button} onPress={handleSetCustomUrl}>
              <Text style={styles.buttonText}>Set Custom URL</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <TouchableOpacity style={styles.button} onPress={showInstructions}>
              <Text style={styles.buttonText}>Show Setup Instructions</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick URLs</Text>
            <TouchableOpacity 
              style={styles.quickButton} 
              onPress={() => setCustomUrl('http://localhost:8000/api/v1')}
            >
              <Text style={styles.quickButtonText}>Localhost (Web/iOS Sim)</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.quickButton} 
              onPress={() => setCustomUrl('http://10.0.2.2:8000/api/v1')}
            >
              <Text style={styles.quickButtonText}>Android Emulator</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>

        <View style={styles.footer}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  container: {
    backgroundColor: '#fff',
    borderRadius: 16,
    margin: 20,
    maxHeight: '80%',
    width: '90%',
  },
  content: {
    padding: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  urlText: {
    fontSize: 14,
    color: '#666',
    backgroundColor: '#f5f5f5',
    padding: 10,
    borderRadius: 8,
    fontFamily: 'monospace',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 10,
    fontFamily: 'monospace',
  },
  button: {
    backgroundColor: '#70A1FF',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  quickButton: {
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    padding: 10,
    marginBottom: 8,
    alignItems: 'center',
  },
  quickButtonText: {
    color: '#333',
    fontSize: 12,
  },
  footer: {
    borderTopWidth: 1,
    borderTopColor: '#eee',
    padding: 15,
  },
  closeButton: {
    backgroundColor: '#ff6b6b',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});