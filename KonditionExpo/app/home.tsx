import React, { useMemo, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Dimensions,} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { router } from 'expo-router';
import { usePersonalBests } from "@/hooks/usePersonalBests";
import { Dialog } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';

const { width } = Dimensions.get('window');
//console.log(" 1 HomeScreen about to be rendered rendered");
const HomeScreen = () => {
  //console.log("2 HomeScreen rendered");
  const { user } = useAuth();
  if (!user) {
    console.warn("User context is undefined");
    return null;
  }
  // 1) Calculate BMI (kg / m²) whenever height or weight change
  //    - height is in cm -> convert to meters by dividing by 100
  //    - weight is in kg, so we can directly use it in the formula
  const bmiValue = useMemo(() => {
    if (!user.height || !user.weight) return null;               
    const heightMeters = user.height / 100;
    if (heightMeters <= 0) return null;                
    const raw = user.weight / (heightMeters * heightMeters);
    return Number(raw.toFixed(1));                     
  }, [user.height, user.weight]);

  // 2) Derive the status string based on BMI ranges
  const bmiStatus = useMemo(() => {
    if (bmiValue === null) return '—'; 
    if (bmiValue < 18.5) return 'Underweight';
    if (bmiValue < 25) return 'Normal Weight';
    if (bmiValue < 30) return 'Overweight';
    if (bmiValue < 35) return 'Obesity Class 1';
    if (bmiValue < 40) return 'Obesity Class 2';
    return 'Obesity Class 3';
  }, [bmiValue]);

  const [showBmiDialog, setShowBmiDialog] = useState(false);

  const workoutProgressData = [20, 40, 30, 60, 90, 80, 70];
  const workoutDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const latestWorkouts = [
    { id: '1', type: 'Fullbody Workout', calories: 180, duration: '20 minutes', icon: require('../assets/images/fullbody.png') },
    { id: '2', type: 'Lowerbody Workout', calories: 200, duration: '30 minutes', icon: require('../assets/images/lowerbody.png') },
    // ... more workouts
  ];
  const { pbs, loading } = usePersonalBests();
  const testPbs = pbs.length === 0 ? [{ metric: "Deadlift", value: 315, date: "2025-05-27" }] : pbs;
  
  console.log('PBS LOADED:', pbs);
  console.log("Rendering personal bests section. pbs:", pbs, "loading:", loading);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.welcomeText}>Welcome Back,</Text>
          <Text style={styles.userName}>{user.full_name}</Text>
          <TouchableOpacity style={styles.notificationBtn} onPress={() => router.push('/notification')}>
            <Image source={require('../assets/images/bell.png')} style={styles.bellIcon} />
          </TouchableOpacity>
        </View>

        {/* ===== BMI Card ===== */}
        <View style={styles.bmiCard}>
          <View style={styles.bmiInfo}>
            <Text style={styles.bmiLabel}>BMI (Body Mass Index)</Text>
            <Text style={styles.bmiStatus}>{bmiStatus}</Text>
            <TouchableOpacity style={styles.viewMoreBtn} onPress={() => setShowBmiDialog(true)}>
              <Text style={styles.viewMoreText}>View More</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.bmiOverlay}>
            <Text style={styles.bmiValue}>{bmiValue !== null ? bmiValue.toString() : '-'}</Text>
          </View>
        </View>

        {/* Today Target */}
        <View style={styles.targetCard}>
          <Text style={styles.targetText}>Today Target</Text>
          <TouchableOpacity style={styles.checkBtn} onPress={() => alert('Targets screen not yet implemented')}>
            <Text style={styles.checkText}>Check</Text>
          </TouchableOpacity>
        </View>

        {/* Workout Progress */}
        <View style={styles.progressSection}>
          <View style={styles.progressHeader}>
            <Text style={styles.sectionTitle}>Workout Progress</Text>
            <TouchableOpacity onPress={() => {/* toggle weekly/monthly */}}>
              <Text style={styles.periodToggle}>Weekly ▼</Text>
            </TouchableOpacity>
          </View>
          <LineChart
            data={{
              labels: workoutDays,
              datasets: [
                {
                  data: workoutProgressData,
                  color: () => '#B07FFD',
                  strokeWidth: 2,
                },
              ],
            }}
            width={width - 64}
            height={100}
            chartConfig={{
              backgroundGradientFrom: '#fff',
              backgroundGradientTo: '#fff',
              color: () => '#B07FFD',
              strokeWidth: 2,
            }}
            bezier
            style={styles.progressChart}
          />
          <View style={styles.daysRow}>
            {workoutDays.map(day => (
              <Text key={day} style={styles.dayText}>{day}</Text>
            ))}
          </View>
        </View>

        {/* Latest Workout */}
        <View style={[styles.latestSection, { backgroundColor: '#f0f0f0' }]}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Latest Workout</Text>
            <TouchableOpacity onPress={() => alert('Workout List not yet implemented')}>
              <Text style={styles.seeMore}>See more</Text>
            </TouchableOpacity>
          </View>
          {latestWorkouts.map(w => (
            <TouchableOpacity key={w.id} style={styles.workoutItem} onPress={() => alert('Workout Details not yet implemented')}>
              <Image source={w.icon} style={styles.workoutIcon} />
              <View style={styles.workoutInfo}>
                <Text style={styles.workoutType}>{w.type}</Text>
                <Text style={styles.workoutMeta}>{w.calories} Calories Burn | {w.duration}</Text>
              </View>
              <Image source={require('../assets/images/arrow-right.png')} style={styles.arrowIcon} />
            </TouchableOpacity>
          ))}
        </View>

        {/* Personal Bests */}
        <View style={[styles.latestSection, { paddingBottom: 16 }]}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Personal Bests</Text>
            <TouchableOpacity onPress={() => alert('Full Personal Bests screen not implemented')}>
              <Text style={styles.seeMore}>See more</Text>
            </TouchableOpacity>
          </View>

          {loading ? (
            <Text style={styles.pbLoading}>Loading personal bests...</Text>
          ) : pbs.length === 0 ? (
            <Text style={styles.pbEmpty}>No personal bests yet. Start training to set new records!</Text>
          ) : (
            testPbs.map((pb) => (
              <View key={pb.exercise_name + pb.date_achieved} style={styles.pbCard}>
                <Image source={require('../assets/images/trophy.png')} style={styles.pbIcon} />
                <View style={styles.pbInfo}>
                  <Text style={styles.pbTitle}>{pb.exercise_name}</Text>
                  <View style={styles.pbDetails}>
                    <Text style={styles.pbValue}>{pb.metric_value} pts</Text>
                    <Text style={styles.pbDate}>{new Date(pb.date_achieved).toLocaleDateString()}</Text>
                  </View>
                </View>
              </View>
            ))
          )}
        </View>



      </ScrollView>
        {/* ─── BMI Disclaimer Dialog ─── */}
        <Dialog
        isOpen={showBmiDialog}
        onClose={() => setShowBmiDialog(false)}
        title="BMI Disclaimer"
        size="sm"
        footer={
          <View style={styles.footer}>
            <Button
              title="OK"
              onPress={() => setShowBmiDialog(false)}
              style={styles.okButton}
            />
          </View>
        }
      >
        <Text style={styles.bodyText}>
          BMI is a screening tool and should not be used as a definitive diagnosis of health problems. 
          It does not take into account factors such as muscle mass, body composition, or age. 
          It is recommended to consult with a healthcare professional for personalized advice on weight management and health.
        </Text>
      </Dialog>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  pbCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  
  pbIcon: {
    width: 40,
    height: 40,
    marginRight: 12,
  },
  
  pbInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  
  pbTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  
  pbDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  
  pbValue: {
    fontSize: 14,
    color: '#70A1FF',
    fontWeight: '500',
  },
  
  pbDate: {
    fontSize: 12,
    color: '#888',
  },    
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  content: { padding: 16, paddingBottom: 80 },
  header: { flexDirection: 'row', alignItems: 'center', marginBottom: 24 },
  welcomeText: { fontSize: 16, color: '#777' },
  userName: { fontSize: 24, fontWeight: 'bold', marginLeft: 8, color: '#333' },
  notificationBtn: { marginLeft: 'auto' },
  bellIcon: { width: 24, height: 24 },
  bmiCard: {
    flexDirection: 'row',
    backgroundColor: '#E5F1FF',
    borderRadius: 20,
    padding: 16,
    alignItems: 'center',
    marginBottom: 24,
  },
  bmiInfo: { flex: 2 },
  bmiLabel: { fontSize: 14, color: '#555' },
  bmiStatus: { fontSize: 16, marginVertical: 4, color: '#333' },
  viewMoreBtn: { backgroundColor: '#70A1FF', borderRadius: 12, paddingVertical: 6, paddingHorizontal: 12, marginTop: 8, alignSelf: 'flex-start' },
  viewMoreText: { color: '#FFF' },
  bmiPie: { height: 100, width: 100, flex: 1 },
  bmiOverlay: { position: 'absolute', right: 32, top: 32, alignItems: 'center' },
  bmiValue: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  footer: { flexDirection: 'row', justifyContent: 'flex-end' },
  okButton: { backgroundColor: '#70A1FF' },
  bodyText: { fontSize: 14, color: '#333', lineHeight: 20 },
  targetCard: { flexDirection: 'row', backgroundColor: '#F5F8FF', borderRadius: 16, padding: 16, alignItems: 'center', marginBottom: 24 },
  targetText: { fontSize: 16, color: '#333' },
  checkBtn: { marginLeft: 'auto', backgroundColor: '#A3C9FD', borderRadius: 12, paddingVertical: 6, paddingHorizontal: 12 },
  checkText: { color: '#FFF' },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 12 },
  activityCard: { backgroundColor: '#F0F6FF', borderRadius: 16, padding: 16, marginBottom: 24 },
  activityLabel: { fontSize: 14, color: '#555' },
  activityValue: { fontSize: 20, fontWeight: 'bold', marginVertical: 8, color: '#333' },
  lineChart: { height: 80, width: '100%' },
  timestampBadge: { position: 'absolute', right: 16, top: 16, backgroundColor: '#FFC0CB', borderRadius: 12, paddingVertical: 4, paddingHorizontal: 8 },
  timestampText: { fontSize: 12, color: '#FFF' },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginBottom: 24 },
  statsCard: { width: '48%', backgroundColor: '#FFF', borderRadius: 16, padding: 16, marginBottom: 16, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 10, elevation: 2 },
  statsCardSmall: { width: '48%', backgroundColor: '#FFF', borderRadius: 16, padding: 16, marginBottom: 16, alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 10, elevation: 2 },
  statsLabel: { fontSize: 14, color: '#555' },
  statsValue: { fontSize: 18, fontWeight: 'bold', marginVertical: 8, color: '#333' },
  calOverlay: { position: 'absolute', top: 28, alignItems: 'center' },
  calOverlayText: { fontSize: 14, fontWeight: 'bold', color: '#FFF' },
  progressSection: { marginBottom: 24 },
  progressHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  periodToggle: { fontSize: 14, color: '#777' },
  progressChart: { height: 100, width: '100%' },
  daysRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 },
  dayText: { fontSize: 12, color: '#777' },
  latestSection: { marginBottom: 24 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  seeMore: { fontSize: 14, color: '#70A1FF' },
  workoutItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#F9FAFF', borderRadius: 16, padding: 12, marginBottom: 12 },
  workoutIcon: { width: 40, height: 40, marginRight: 12 },
  workoutInfo: { flex: 1 },
  workoutType: { fontSize: 16, fontWeight: 'bold', color: '#333' },
  workoutMeta: { fontSize: 12, color: '#777', marginTop: 4 },
  arrowIcon: { width: 24, height: 24, tintColor: '#777' },
});

export default HomeScreen;
