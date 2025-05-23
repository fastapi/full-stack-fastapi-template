import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
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
  const [heightFeet, setHeightFeet] = useState('');
  const [heightInches, setHeightInches] = useState('');


  const ddRef = useRef<TextInput>(null);
  const yyyyRef = useRef<TextInput>(null);

  const onChangeDobMM = (text: string) => {
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

  const handleNext = () => {
    const mm = parseInt(dobMM, 10);
    const dd = parseInt(dobDD, 10);
    const yyyy = parseInt(dobYYYY, 10);
    const currentYear = new Date().getFullYear();
  
    if (!gender || !dobMM || !dobDD || !dobYYYY || !weight || 
      (heightUnit === 'ft/in' && (!heightFeet || !heightInches)) ||
      (heightUnit === 'cm' && !height)
    ) {
      alert('Please fill out all fields');
      return;
    }
  
    if (mm < 1 || mm > 12) {
      alert('Month must be between 1 and 12');
      return;
    }
  
    if (dd < 1 || dd > 31) {
      alert('Day must be between 1 and 31');
      return;
    }
  
    if (yyyy < 1900 || yyyy > currentYear) {
      alert(`Year must be between 1900 and ${currentYear}`);
      return;
    }
  
    router.replace('/home');
  };
  
  

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={64}
    >
      <ScrollView contentContainerStyle={styles.contentContainer}>
        <Text style={styles.title}>Additional Info</Text>

        {/* Gender */}
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

        {/* DOB */}
        <Text style={styles.label}>Date of Birth</Text>
        <Text style={styles.subLabel}>MM / DD / YYYY</Text>
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
            placeholderTextColor="#999"
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
            placeholderTextColor="#999"
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
            placeholderTextColor="#999"
          />
        </View>

        {/* Weight */}
      <Text style={styles.label}>Weight</Text>
      <View style={styles.row}>
        <TextInput
          style={[styles.textInput, { flex: 1, backgroundColor: 'white' }]}
          value={weight}
          onChangeText={(text) => {
            const clean = text.replace(/[^0-9]/g, '');
            setWeight(clean);
          }}
          keyboardType="numeric"
          placeholder="Enter weight"
          placeholderTextColor="#888"
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

      {/* Height */}
      <Text style={styles.label}>Height</Text>
      <View style={styles.row}>
        {heightUnit === 'ft/in' ? (
          <>
            <TextInput
              style={[styles.textInput, { flex: 1, backgroundColor: 'white' }]}
              value={heightFeet}
              onChangeText={(text) => {
                const clean = text.replace(/[^0-9]/g, '');
                setHeightFeet(clean);
              }}
              keyboardType="numeric"
              placeholder="Feet"
              placeholderTextColor="#888"
            />
            <TextInput
              style={[styles.textInput, { flex: 1, marginLeft: 10, backgroundColor: 'white' }]}
              value={heightInches}
              onChangeText={(text) => {
                const clean = text.replace(/[^0-9]/g, '');
                setHeightInches(clean);
              }}
              keyboardType="numeric"
              placeholder="Inches"
              placeholderTextColor="#888"
            />
          </>
        ) : (
          <TextInput
            style={[styles.textInput, { flex: 1, backgroundColor: 'white' }]}
            value={height}
            onChangeText={(text) => {
              const clean = text.replace(/[^0-9]/g, '');
              setHeight(clean);
            }}
            keyboardType="numeric"
            placeholder="Height in cm"
            placeholderTextColor="#888"
          />
        )}
        <RNPickerSelect
          onValueChange={(val) => {
            setHeightUnit(val);
            // Reset fields on switch
            setHeight('');
            setHeightFeet('');
            setHeightInches('');
          }}
          value={heightUnit}
          items={[
            { label: 'ft/in', value: 'ft/in' },
            { label: 'cm', value: 'cm' },
          ]}
          style={pickerSelectStylesSmall}
        />
      </View>


        {/* Submit */}
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 24,
    textAlign: 'center',
  },
  label: {
    fontSize: 16,
    marginBottom: 4,
    marginTop: 16,
    color: 'white',
  },
  subLabel: {
    fontSize: 14,
    marginBottom: 8,
    color: '#aaa',
  },
  dobRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dobInput: {
    borderWidth: 1,
    borderColor: '#ccc',
    backgroundColor: 'white',
    padding: 10,
    borderRadius: 6,
    fontSize: 16,
    textAlign: 'center',
    color: 'black',
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
    color: 'white',
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
    backgroundColor: 'white',
    color: 'black',
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
    backgroundColor: 'white',
    paddingRight: 30,
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
    backgroundColor: 'white',
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
    backgroundColor: 'white',
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
    backgroundColor: 'white',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
  },
};
