import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, TextInput, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import RNPickerSelect from 'react-native-picker-select';
import { Button } from '@/components/ui/Button';
import { router } from 'expo-router';

export default function SignUpStep2() {
  const [gender, setGender] = useState('');
  
  // DOB parts
  const [dobMM, setDobMM] = useState('');
  const [dobDD, setDobDD] = useState('');
  const [dobYYYY, setDobYYYY] = useState('');
  
  // Weight + units
  const [weight, setWeight] = useState('');
  const [weightUnit, setWeightUnit] = useState('lbs');
  
  // Height + units
  const [height, setHeight] = useState('');
  const [heightUnit, setHeightUnit] = useState('ft/in');

  // refs for DOB inputs to auto-focus next field
  const ddRef = useRef<TextInput>(null);
  const yyyyRef = useRef<TextInput>(null);

  // Handle DOB input with auto-advance
  const onChangeDobMM = (text: string) => {
    // Allow only digits, max 2 chars
    const cleanText = text.replace(/[^0-9]/g, '').slice(0, 2);
    setDobMM(cleanText);
    if (cleanText.length === 2) {
      ddRef.current?.focus();
    }
  };

  const onChangeDobDD = (text: string) => {
    const cleanText = text.replace(/[^0-9]/g, '').slice(0, 2);
    setDobDD(cleanText);
    if (cleanText.length === 2) {
      yyyyRef.current?.focus();
    }
  };

  const onChangeDobYYYY = (text: string) => {
    const cleanText = text.replace(/[^0-9]/g, '').slice(0, 4);
    setDobYYYY(cleanText);
  };

  // Submit handler
  const handleNext = () => {
    // Add your validation & submit logic here
    if (!gender || !dobMM || !dobDD || !dobYYYY || !weight || !height) {
      alert('Please fill out all fields');
      return;
    }
    // Proceed to next screen or API call
    router.replace('/(tabs)');
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.contentContainer}>
        <Text style={styles.title}>Additional Info</Text>

        <Text style={styles.label}>Gender</Text>
        <RNPickerSelect
          onValueChange={setGender}
          value={gender}
          placeholder={{ label: 'Select Gender...', value: '' }}
          items={[
            { label: 'Male', value: 'male' },
            { label: 'Female', value: 'female' },
            { label: 'Non-binary', value: 'non-binary' },
            { label: 'Other', value: 'other' },
          ]}
          style={pickerSelectStyles}
        />

        <Text style={styles.label}>Date of Birth (MM/DD/YYYY)</Text>
        <View style={styles.dobRow}>
          <TextInput
            style={[styles.dobInput, styles.dobPart]}
            value={dobMM}
            onChangeText={onChangeDobMM}
            keyboardType="numeric"
            maxLength={2}
            placeholder="MM"
            returnKeyType="next"
            blurOnSubmit={false}
            onSubmitEditing={() => ddRef.current?.focus()}
          />
          <Text style={styles.slash}>/</Text>
          <TextInput
            ref={ddRef}
            style={[styles.dobInput, styles.dobPart]}
            value={dobDD}
            onChangeText={onChangeDobDD}
            keyboardType="numeric"
            maxLength={2}
            placeholder="DD"
            returnKeyType="next"
            blurOnSubmit={false}
            onSubmitEditing={() => yyyyRef.current?.focus()}
          />
          <Text style={styles.slash}>/</Text>
          <TextInput
            ref={yyyyRef}
            style={[styles.dobInput, styles.dobYear]}
            value={dobYYYY}
            onChangeText={onChangeDobYYYY}
            keyboardType="numeric"
            maxLength={4}
            placeholder="YYYY"
            returnKeyType="done"
          />
        </View>

        <Text style={styles.label}>Weight</Text>
        <View style={styles.row}>
          <TextInput
            style={[styles.textInput, { flex: 1 }]}
            value={weight}
            onChangeText={setWeight}
            keyboardType="numeric"
            placeholder="Enter weight"
          />
          <RNPickerSelect
            onValueChange={setWeightUnit}
            value={weightUnit}
            items={[
              { label: 'lbs', value: 'lbs' },
              { label: 'kg', value: 'kg' },
            ]}
            style={pickerSelectStylesSmall}
          />
        </View>

        <Text style={styles.label}>Height</Text>
        <View style={styles.row}>
          <TextInput
            style={[styles.textInput, { flex: 1 }]}
            value={height}
            onChangeText={setHeight}
            keyboardType="numeric"
            placeholder={`Enter height in ${heightUnit === 'ft/in' ? 'feet/inches' : 'cm'}`}
          />
          <RNPickerSelect
            onValueChange={setHeightUnit}
            value={heightUnit}
            items={[
              { label: 'ft/in', value: 'ft/in' },
              { label: 'cm', value: 'cm' },
            ]}
            style={pickerSelectStylesSmall}
          />
        </View>

        <Button title="Next" onPress={handleNext} fullWidth style={{ marginTop: 30 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  contentContainer: {
    padding: 24,
    justifyContent: 'center',
  },
  title: { fontSize: 24, fontWeight: 'bold', marginBottom: 24, textAlign: 'center' },
  label: { fontSize: 16, marginBottom: 8, marginTop: 16 },
  dobRow: { flexDirection: 'row', alignItems: 'center' },
  dobInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    borderRadius: 6,
    fontSize: 16,
    textAlign: 'center',
  },
  dobPart: {
    width: 50,
  },
  dobYear: {
    flex: 1,
  },
  slash: {
    fontSize: 18,
    marginHorizontal: 5,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    padding: 10,
    fontSize: 16,
  },
});

const pickerSelectStyles = {
  inputIOS: {
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    color: 'black',
    paddingRight: 30, // to ensure the text is never behind the icon
    marginBottom: 8,
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    color: 'black',
    paddingRight: 30,
    marginBottom: 8,
  },
};

const pickerSelectStylesSmall = {
  inputIOS: {
    fontSize: 16,
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    color: 'black',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 6,
    color: 'black',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
  },
};
