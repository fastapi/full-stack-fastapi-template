import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, FlatList, Image } from 'react-native';
/*
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const notifications = [
  { id: '1', title: "Hey, it's time for lunch", time: 'About 1 minute ago', icon: require('./assets/lunch.png') },
  { id: '2', title: "Don't miss your lowerbody workout", time: 'About 3 hours ago', icon: require('./assets/workout.png') },
  { id: '3', title: "Hey, let's add some meals for your b..", time: 'About 3 hours ago', icon: require('./assets/meals.png') },
  { id: '4', title: 'Congratulations, You have finished A..', time: '29 May', icon: require('./assets/congrats.png') },
  { id: '5', title: "Hey, it's time for lunch", time: '8 April', icon: require('./assets/lunch.png') },
  { id: '6', title: 'Ups, You have missed your Lowerbo..', time: '3 April', icon: require('./assets/workout.png') },
];
*/

export default function NotificationScreen({ navigation }) {
  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Image source={item.icon} style={styles.itemIcon} />
      <View style={styles.itemText}>
        <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
        <Text style={styles.time}>{item.time}</Text>
      </View>
      <TouchableOpacity style={styles.itemMenu}>
        <Icon name="dots-vertical" size={20} />
      </TouchableOpacity>
    </View>
  );
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-left" size={24} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Notification</Text>
        <TouchableOpacity>
          <Icon name="dots-horizontal" size={24} />
        </TouchableOpacity>
      </View>
      <FlatList
        data={notifications}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16 },
  headerTitle: { fontSize: 18, fontWeight: 'bold' },
  item: { flexDirection: 'row', alignItems: 'center', padding: 16 },
  itemIcon: { width: 40, height: 40, borderRadius: 20 },
  itemText: { flex: 1, marginLeft: 12 },
  title: { fontSize: 16 },
  time: { fontSize: 12, color: '#888' },
  itemMenu: { padding: 8 },
  separator: { height: 1, backgroundColor: '#eee', marginLeft: 68 },
});
