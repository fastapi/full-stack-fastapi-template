import React, { useState } from 'react';
import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Switch } from 'react-native';
import { useUser } from '@/contexts/UserContext';
import { useAuth } from '@/contexts/AuthContext';
import { router } from 'expo-router';
import { DevTools } from '@/components/DevTools';
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';

const ProfileScreen = () => {
  const { name, height, weight, age } = useUser();
  const { user, logout, isLoading } = useAuth();
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [showDevTools, setShowDevTools] = useState(false);
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);

  const toggleNotifications = () => setNotificationsEnabled(prev => !prev);

  const handleLogout = () => {
    setShowLogoutDialog(true);
  };

  const confirmLogout = async () => {
    try {
      console.log('Starting logout process...');
      setShowLogoutDialog(false);
      await logout();
      console.log('Logout successful');
      // Navigation will be handled automatically by ProtectedRoute
    } catch (error) {
      console.error('Logout error:', error);
      // For web compatibility, we'll use a simple alert or could create another dialog
      if (typeof window !== 'undefined') {
        // Web environment
        alert(`Failed to sign out: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`);
      } else {
        // Mobile environment - this shouldn't happen but as fallback
        console.error('Logout failed:', error);
      }
    }
  };

  const cancelLogout = () => {
    setShowLogoutDialog(false);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Profile Box */}
        <View style={styles.profileBox}>
          <Text style={styles.profileName}>{user?.full_name || name || 'User'}</Text>
          <Text style={styles.profileEmail}>{user?.email || 'No email'}</Text>
          <TouchableOpacity style={styles.editBtn}>
            <Text style={styles.editText}>Edit</Text>
          </TouchableOpacity>

          <View style={styles.statsRow}>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>Height</Text>
              <Text style={styles.statValue}>{height ? `${height} cm` : '-'}</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>Weight</Text>
              <Text style={styles.statValue}>{weight ? `${weight} kg` : '-'}</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>Age</Text>
              <Text style={styles.statValue}>{age > 0 ? age.toString() : '-'}</Text>
            </View>
          </View>
        </View>

        {/* Account Box */}
        <View style={styles.sectionBox}>
          <Text style={styles.sectionTitle}>Account</Text>
          <Text style={styles.optionItem}>Personal Data</Text>
          <Text style={styles.optionItem}>Achievement</Text>
          <Text style={styles.optionItem}>Activity History</Text>
          <Text style={styles.optionItem}>Workout Progress</Text>
        </View>

        {/* Notification Box */}
        <View style={styles.sectionBox}>
          <Text style={styles.sectionTitle}>Notification</Text>
          <View style={styles.toggleRow}>
            <Text style={styles.optionItem}>Pop-up Notifications</Text>
            <Switch
              value={notificationsEnabled}
              onValueChange={toggleNotifications}
              trackColor={{ false: '#ccc', true: '#70A1FF' }}
              thumbColor={notificationsEnabled ? '#FFF' : '#f4f3f4'}
            />
          </View>
        </View>

        {/* Other Box */}
        <View style={styles.sectionBox}>
          <Text style={styles.sectionTitle}>Other</Text>
          <Text style={styles.optionItem}>Privacy Policy</Text>
          <Text style={styles.optionItem}>Contact Us</Text>
          <Text style={styles.optionItem}>Settings</Text>
          <TouchableOpacity onPress={() => setShowDevTools(true)}>
            <Text style={[styles.optionItem, { color: '#70A1FF' }]}>Developer Tools</Text>
          </TouchableOpacity>
        </View>

        {/* Logout Button */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
          disabled={isLoading}
        >
          <Text style={styles.logoutText}>
            {isLoading ? 'Signing Out...' : 'Sign Out'}
          </Text>
        </TouchableOpacity>
      </ScrollView>

      {/* DevTools Modal */}
      <DevTools
        visible={showDevTools}
        onClose={() => setShowDevTools(false)}
      />

      {/* Logout Confirmation Dialog */}
      <Dialog
        isOpen={showLogoutDialog}
        onClose={cancelLogout}
        title="Sign Out"
        size="sm"
        footer={
          <View style={styles.dialogFooter}>
            <Button
              title="Cancel"
              variant="outline"
              onPress={cancelLogout}
              style={styles.cancelButton}
            />
            <Button
              title="Sign Out"
              onPress={confirmLogout}
              loading={isLoading}
              loadingText="Signing Out..."
              style={styles.confirmButton}
            />
          </View>
        }
      >
        <Text style={styles.dialogText}>
          Are you sure you want to sign out?
        </Text>
      </Dialog>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  content: { padding: 16, paddingBottom: 80 },
  profileBox: { backgroundColor: '#E5F1FF', borderRadius: 20, padding: 16, marginBottom: 24 },
  profileName: { fontSize: 24, fontWeight: 'bold', color: '#333' },
  profileEmail: { fontSize: 14, color: '#666', marginTop: 4 },
  editBtn: { backgroundColor: '#70A1FF', borderRadius: 12, paddingVertical: 6, paddingHorizontal: 12, alignSelf: 'flex-start', marginTop: 8 },
  editText: { color: '#FFF' },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 16 },
  statBox: { backgroundColor: '#FFF', borderRadius: 12, padding: 12, width: '30%', alignItems: 'center' },
  statLabel: { fontSize: 12, color: '#555' },
  statValue: { fontSize: 16, fontWeight: 'bold', color: '#333' },
  sectionBox: { backgroundColor: '#F5F8FF', borderRadius: 16, padding: 16, marginBottom: 24 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#333', marginBottom: 8 },
  optionItem: { fontSize: 14, color: '#555', paddingVertical: 6 },
  toggleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  logoutButton: {
    backgroundColor: '#FF6B6B',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 24
  },
  logoutText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold'
  },
  dialogFooter: {
    flexDirection: 'row',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
  },
  confirmButton: {
    flex: 1,
    backgroundColor: '#FF6B6B',
  },
  dialogText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    lineHeight: 24,
  },
});

export default ProfileScreen; 