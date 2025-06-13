  import React from 'react';
import { useUser } from '@/contexts/UserContext';
import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Image, Dimensions } from 'react-native';
import { LineChart, PieChart } from 'react-native-chart-kit';
import { router } from 'expo-router';
import { usePersonalBests } from "@/hooks/usePersonalBests";
import { getAccessToken } from '@/scripts/auth';
import { useEffect } from 'react';



const { width } = Dimensions.get('window');
//console.log(" 1 HomeScreen about to be rendered rendered");
const HomeScreen = () => {
  //console.log("2 HomeScreen rendered");
  // TODO: Replace with real data
  const bmiValue = '20.1';
  const user = useUser();
  if (!user) {
    console.warn("User context is undefined");
    return null;
  }
  const { name } = user;
  useEffect(() => {
    const fetchAdminDbStructure = async () => {
      try {
        const token = await getAccessToken();
        const res = await fetch('http://localhost:8000/api/v1/inspect-db', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
  
        if (!res.ok) {
          console.error(`Failed to fetch admin DB structure: ${res.status}`);
          return;
        }
  
        const dbStructure = await res.json();
        console.log("🛠 Admin DB Structure:", dbStructure);
      } catch (err) {
        console.error("Error fetching admin DB structure:", err);
      }
    };
  
    fetchAdminDbStructure();
  }, []);
  const heartRateData = [60, 62, 65, 70, 75, 78, 80, 82, 79, 76];
  const waterIntake = '4L';
  const sleepHours = '8h 20m';
  const caloriesBurnt = 760;
  const caloriesLeft = 230;
  const workoutProgressData = [20, 40, 30, 60, 90, 80, 70];
  const workoutDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const latestWorkouts = [
    { id: '1', type: 'Fullbody Workout', calories: 180, duration: '20 minutes', icon: require('../assets/images/fullbody.png') },
    { id: '2', type: 'Lowerbody Workout', calories: 200, duration: '30 minutes', icon: require('../assets/images/lowerbody.png') },
    // ... more workouts
  ];
  const { pbs = [], loading } = usePersonalBests();
  const testPbs = pbs.length === 0 ? [{ metric: "Deadlift", value: 315, date: "2025-05-27" }] : pbs;
  
  console.log('PBS LOADED:', pbs);
  console.log("Rendering personal bests section. pbs:", pbs, "loading:", loading);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.welcomeText}>Welcome Back,</Text>
          <Text style={styles.userName}>{name}</Text>
          <TouchableOpacity style={styles.notificationBtn} onPress={() => router.push('/notification')}>
            <Image source={require('../assets/images/bell.png')} style={styles.bellIcon} />
          </TouchableOpacity>
        </View>

        {/* BMI Card */}
        <View style={styles.bmiCard}>
          <View style={styles.bmiInfo}>
            <Text style={styles.bmiLabel}>BMI (Body Mass Index)</Text>
            <Text style={styles.bmiStatus}>You have a normal weight</Text>
            <TouchableOpacity style={styles.viewMoreBtn} onPress={() => alert('BMI screen not yet implemented')}>
              <Text style={styles.viewMoreText}>View More</Text>
            </TouchableOpacity>
          </View>
          <PieChart
            data={[
              { name: 'BMI', population: parseFloat(bmiValue), color: '#A3C9FD', legendFontColor: '#7F7F7F', legendFontSize: 15 },
              { name: 'Other', population: 30 - parseFloat(bmiValue), color: '#E5EFFF', legendFontColor: '#7F7F7F', legendFontSize: 15 },
            ]}
            width={100}
            height={100}
            chartConfig={{
              color: (opacity = 1) => `rgba(163, 201, 253, ${opacity})`,
            }}
            accessor={'population'}
            backgroundColor={'transparent'}
            paddingLeft={'0'}
            hasLegend={false}
            center={[0, 0]}
          />
          <View style={styles.bmiOverlay}>
            <Text style={styles.bmiValue}>{bmiValue}</Text>
          </View>
        </View>

        {/* Today Target */}
        <View style={styles.targetCard}>
          <Text style={styles.targetText}>Today Target</Text>
          <TouchableOpacity style={styles.checkBtn} onPress={() => alert('Targets screen not yet implemented')}>
            <Text style={styles.checkText}>Check</Text>
          </TouchableOpacity>
        </View>

        {/* Activity Status */}
        <Text style={styles.sectionTitle}>Activity Status</Text>
        <View style={styles.activityCard}>
          <Text style={styles.activityLabel}>Heart Rate</Text>
          <Text style={styles.activityValue}>78 BPM</Text>
          <LineChart
            data={{
              labels: [],
              datasets: [
                {
                  data: heartRateData,
                  color: () => '#91D5A1',
                  strokeWidth: 2,
                },
              ],
            }}
            width={width - 64}
            height={100}
            chartConfig={{
              backgroundGradientFrom: '#fff',
              backgroundGradientTo: '#fff',
              color: () => '#91D5A1',
              strokeWidth: 2,
            }}
            bezier
            style={styles.lineChart}
          />
          <View style={styles.timestampBadge}>
            <Text style={styles.timestampText}>3 mins ago</Text>
          </View>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <View style={styles.statsCard}>
            <Text style={styles.statsLabel}>Water Intake</Text>
            <Text style={styles.statsValue}>{waterIntake}</Text>
          </View>
          <View style={styles.statsCard}>
            <Text style={styles.statsLabel}>Sleep</Text>
            <Text style={styles.statsValue}>{sleepHours}</Text>
          </View>
          <View style={styles.statsCardSmall}>
            <Text style={styles.statsLabel}>Calories</Text>
            <Text style={styles.statsValue}>{caloriesBurnt} kCal</Text>
            <PieChart
              data={[
                { name: 'Burnt', population: caloriesBurnt, color: '#FFC069', legendFontColor: '#7F7F7F', legendFontSize: 15 },
                { name: 'Left', population: caloriesLeft, color: '#FFECCE', legendFontColor: '#7F7F7F', legendFontSize: 15 },
              ]}
              width={80}
              height={80}
              chartConfig={{
                color: (opacity = 1) => `rgba(255, 192, 105, ${opacity})`,
              }}
              accessor={'population'}
              backgroundColor={'transparent'}
              paddingLeft={'0'}
              hasLegend={false}
              center={[0, 0]}
            />
            <View style={styles.calOverlay}>
              <Text style={styles.calOverlayText}>{caloriesLeft} kCal</Text>
            </View>
          </View>
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
            <Text style={{ textAlign: 'center', color: '#666', marginBottom: 12 }}>Loading personal bests...</Text>
          ) : pbs.length === 0 ? (
            <Text style={{ textAlign: 'center', color: '#999', marginBottom: 12 }}>No personal bests yet. Start training to set new records!</Text>
          ) : (
            pbs.map((pb) => (
              <View key={pb.metric} style={styles.workoutItem}>
                <Image source={require('../assets/images/trophy.png')} style={styles.workoutIcon} />
                <View style={styles.workoutInfo}>
                  <Text style={styles.workoutType}>{pb.metric}</Text>
                  <Text style={styles.workoutMeta}>{pb.value} • {pb.date}</Text>
                </View>
              </View>
            ))
          )}
        </View>


      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
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
