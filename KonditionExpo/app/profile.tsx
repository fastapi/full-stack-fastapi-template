import React, { useState } from 'react';
import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Switch } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { router } from 'expo-router';

const ProfileScreen = () => {
  const { user } = useAuth();
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  const toggleNotifications = () => setNotificationsEnabled(prev => !prev);

  // Calculate age from date of birth
  const calculateAge = (dateOfBirth: string | undefined): number => {
    if (!dateOfBirth) return 0;
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const age = calculateAge(user?.date_of_birth);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Back Arrow */}
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Image source={require('@/assets/images/arrow-left.png')} style={styles.backIcon} />
        </TouchableOpacity>

        {/* Profile Box */}
        <View style={styles.profileBox}>
          <Text style={styles.profileName}>{user?.full_name || user?.email || 'User'}</Text>
          <TouchableOpacity style={styles.editBtn}>
            <Text style={styles.editText}>Edit</Text>
          </TouchableOpacity>

          <View style={styles.statsRow}>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>Height</Text>
              <Text style={styles.statValue}>{user?.height ? `${user.height} cm` : '-'}</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statLabel}>Weight</Text>
              <Text style={styles.statValue}>{user?.weight ? `${user.weight} kg` : '-'}</Text>
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
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  content: { padding: 16, paddingBottom: 80 },
  backBtn: { marginBottom: 16 },
  backIcon: { width: 24, height: 24 },
  profileBox: { backgroundColor: '#E5F1FF', borderRadius: 20, padding: 16, marginBottom: 24 },
  profileName: { fontSize: 24, fontWeight: 'bold', color: '#333' },
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
});

export default ProfileScreen;
