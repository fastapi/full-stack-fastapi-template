import React, { useState } from 'react';
import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Switch } from 'react-native';
import { useUser } from '@/contexts/UserContext';
import { router } from 'expo-router';

const ProfileScreen = () => {
  const { name, height, weight, age } = useUser();
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  const toggleNotifications = () => setNotificationsEnabled(prev => !prev);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Back Arrow */}
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Image source={require('@/assets/images/arrow-left.png')} style={styles.backIcon} />
        </TouchableOpacity>

        {/* Profile Box */}
        <View style={styles.profileBox}>
          <Text style={styles.profileName}>{name || 'User'}</Text>
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
              <Text style={styles.statValue}>{age > 0 ? age : '-'}</Text>
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

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity onPress={() => router.replace('/home')}>
          <Image source={require('../assets/images/home-active.png')} style={styles.navIcon} />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => alert('Progress screen not yet implemented')}>
          <Image source={require('../assets/images/chart.png')} style={styles.navIcon} />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => alert('Search screen not yet implemented')}>
          <Image source={require('../assets/images/search.png')} style={styles.searchIcon} />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => alert('Camera screen not yet implemented')}>
          <Image source={require('../assets/images/camera.png')} style={styles.navIcon} />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => router.replace('/home')}>
          <Image source={require('../assets/images/user.png')} style={styles.navIcon} />
        </TouchableOpacity>
      </View>
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
  bottomNav: { position: 'absolute', bottom: 0, left: 0, right: 0, height: 60, flexDirection: 'row', justifyContent: 'space-around', alignItems: 'center', backgroundColor: '#FFF', borderTopWidth: 1, borderColor: '#EEE' },
  navIcon: { width: 24, height: 24 },
  searchIcon: { width: 28, height: 28 },
});

export default ProfileScreen;
