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
import { useUser } from '@/contexts/UserContext';
import { TouchableWithoutFeedback, Keyboard } from 'react-native';


export default function SignUpStep2() {
  const [gender, setGender] = useState('');
  const { setHeight, setWeight, setAge } = useUser();

  const [dobMM, setDobMM] = useState('');
  const [dobDD, setDobDD] = useState('');
  const [dobYYYY, setDobYYYY] = useState('');

  const [weight, updateWeight] = useState('');
  const [weightUnit, setWeightUnit] = useState('lbs');

  const [height, updateHeight] = useState('');
  const [heightUnit, setHeightUnit] = useState('ft/in');
  const [heightFeet, setHeightFeet] = useState('');
  const [heightInches, setHeightInches] = useState('');

  const ddRef = useRef<TextInput>(null);
  const yyyyRef = useRef<TextInput>(null);

  const onChangeDobMM = (text: string) => {
    const cleanText = text.replace(/[^0-9]/g, '').slice(0, 2);
    setDobMM(cleanText);
    if (cleanText.length === 2) ddRef.current?.focus();
  };

  const onChangeDobDD = (text: string) => {
    const cleanText = text.replace(/[^0-9]/g, '').slice(0, 2);
    setDobDD(cleanText);
    if (cleanText.length === 2) yyyyRef.current?.focus();
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

    const birthDate = new Date(yyyy, mm - 1, dd);
    const today = new Date();
    let calculatedAge = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      calculatedAge--;
    }

    let heightInCm = '';
    if (heightUnit === 'ft/in') {
      const feet = parseInt(heightFeet, 10) || 0;
      const inches = parseInt(heightInches, 10) || 0;
      heightInCm = Math.round(feet * 30.48 + inches * 2.54).toString();
    } else {
      heightInCm = height;
    }

    let weightInKg = '';
    if (weightUnit === 'lbs') {
      weightInKg = (parseFloat(weight) * 0.453592).toFixed(1);
    } else {
      weightInKg = weight;
    }

    // Save values to context
    setAge(calculatedAge);
    setHeight(heightInCm);
    setWeight(weightInKg);

    router.replace('/(tabs)');
  };

  return (
    <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={64}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <ScrollView contentContainerStyle={styles.contentContainer} keyboardShouldPersistTaps="handled" style={{ flex: 1, overflow: 'visible' }}>
          <Text style={styles.title}>Additional Info</Text>

          <Text style={styles.label}>Gender</Text>
          <View style={styles.pickerContainer}>
          <RNPickerSelect
            onValueChange={(val) => {
              setGender(val);
            }}
            value={gender}
            placeholder={{ label: 'Select Gender...', value: '' }}
            items={[
              { label: 'Male', value: 'male' },
              { label: 'Female', value: 'female' },
              { label: 'Non-binary', value: 'non-binary' },
              { label: 'Other', value: 'other' },
            ]}
            style={pickerSelectStyles}
            useNativeAndroidPickerStyle={false}
            onOpen={() => Keyboard.dismiss}
          /></View>

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
              placeholderTextColor="#aaa"
              returnKeyType="done"
              blurOnSubmit={true}
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
              placeholderTextColor="#aaa"
              returnKeyType="done"
              blurOnSubmit={true}
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
              placeholderTextColor="#aaa"
              returnKeyType="done"
              blurOnSubmit={true}
            />
          </View>

          <Text style={styles.label}>Weight</Text>
          <View style={styles.row}>
            <TextInput
              style={styles.textInput}
              value={weight}
              onChangeText={(text) => updateWeight(text.replace(/[^0-9]/g, ''))}
              keyboardType="numeric"
              placeholder="Enter weight"
              placeholderTextColor="#aaa"
              returnKeyType="done"
              blurOnSubmit={true}
            />
            <View style={styles.pickerContainer}>
            <RNPickerSelect
              onValueChange={setWeightUnit}
              value={weightUnit}
              items={[
                { label: 'lbs', value: 'lbs' },
                { label: 'kg', value: 'kg' },
              ]}
              style={pickerSelectStylesSmall}
              useNativeAndroidPickerStyle={false}
              onOpen={() => Keyboard.dismiss()}
            /></View>
          </View>

          <Text style={styles.label}>Height</Text>
          <View style={styles.row}>
            {heightUnit === 'ft/in' ? (
              <>
                <TextInput
                  style={styles.textInput}
                  value={heightFeet}
                  onChangeText={(text) => setHeightFeet(text.replace(/[^0-9]/g, ''))}
                  keyboardType="numeric"
                  placeholder="Feet"
                  placeholderTextColor="#aaa"
                  returnKeyType="done"
                  blurOnSubmit={true}
                />
                <TextInput
                  style={[styles.textInput, { marginLeft: 10 }]}
                  value={heightInches}
                  onChangeText={(text) => setHeightInches(text.replace(/[^0-9]/g, ''))}
                  keyboardType="numeric"
                  placeholder="Inches"
                  placeholderTextColor="#aaa"
                  returnKeyType="done"
                  blurOnSubmit={true}
                />
              </>
            ) : (
              <TextInput
                style={styles.textInput}
                value={height}
                onChangeText={(text) => updateHeight(text.replace(/[^0-9]/g, ''))}
                keyboardType="numeric"
                placeholder="Height in cm"
                placeholderTextColor="#aaa"
                returnKeyType="done"
                blurOnSubmit={true}
              />
            )}
            <View style={styles.pickerContainer}>
            <RNPickerSelect
              onValueChange={(val) => {
                setHeightUnit(val);
                updateHeight('');
                setHeightFeet('');
                setHeightInches('');
              }}
              value={heightUnit}
              items={[
                { label: 'ft/in', value: 'ft/in' },
                { label: 'cm', value: 'cm' },
              ]}
              style={pickerSelectStylesSmall}
              useNativeAndroidPickerStyle={false}
              onOpen={() => Keyboard.dismiss()}
            /></View>
          </View>

          <Button title="Next" onPress={handleNext} fullWidth style={{ marginTop: 30 }} />
        </ScrollView>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>

  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#101010' },
  contentContainer: { padding: 24 },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: 'white',
    marginBottom: 24,
    textAlign: 'center',
    fontFamily: 'System',
  },
  label: {
    fontSize: 18,
    color: 'white',
    marginTop: 16,
    marginBottom: 4,
    fontFamily: 'System',
  },
  subLabel: {
    fontSize: 14,
    color: '#bbb',
    marginBottom: 8,
  },
  dobRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  dobInput: {
    borderWidth: 1,
    borderColor: '#555',
    backgroundColor: '#1a1a1a',
    padding: 10,
    borderRadius: 6,
    fontSize: 16,
    textAlign: 'center',
    color: 'white',
  },
  dobPart: {
    width: 50,
  },
  dobYear: {
    flex: 1,
  },
  slash: {
    fontSize: 18,
    color: 'white',
    marginHorizontal: 5,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 6,
    padding: 10,
    fontSize: 16,
    backgroundColor: '#1a1a1a',
    color: 'white',
    fontFamily: 'System',
  },
  pickerContainer: {
    height: 48,
    justifyContent: 'center',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 6,
    backgroundColor: '#1a1a1a',
  },
});

const pickerSelectStyles = {
  inputIOS: {
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 10,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 6,
    color: 'white',
    backgroundColor: '#1a1a1a',
    paddingRight: 30,
    marginBottom: 8,
    flex: 1,
    justifyContent: 'center',
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 6,
    color: 'white',
    backgroundColor: '#1a1a1a',
    paddingRight: 30,
    marginBottom: 8,
    justifyContent: 'center',
  },
};

const pickerSelectStylesSmall = {
  inputIOS: {
    fontSize: 16,
    paddingVertical: 10,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 6,
    color: 'white',
    backgroundColor: '#1a1a1a',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
    minHeight: 44,
    justifyContent: 'center'
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 6,
    color: 'white',
    backgroundColor: '#1a1a1a',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
    minHeight: 44,
    justifyContent: 'center',
  },
};
