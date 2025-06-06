import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  TouchableOpacity,
} from 'react-native';
import RNPickerSelect from 'react-native-picker-select';
import { Button } from '@/components/ui/Button';
import { router } from 'expo-router';
import { useAuth } from '@/contexts/AuthContext';
import { useThemeColor } from '../hooks/useThemeColor';

export default function SignUpStep2() {
  const { updateProfile, isLoading, isAuthenticated, user, setSignupFlowComplete } = useAuth();
  const [gender, setGender] = useState('');
  const [dobMM, setDobMM] = useState('');
  const [dobDD, setDobDD] = useState('');
  const [dobYYYY, setDobYYYY] = useState('');
  const [weight, setWeight] = useState('');
  const [weightUnit, setWeightUnit] = useState('lbs');
  const [height, setHeight] = useState('');
  const [heightUnit, setHeightUnit] = useState('ft/in');
  const [heightFeet, setHeightFeet] = useState('');
  const [heightInches, setHeightInches] = useState('');
  const [errors, setErrors] = useState<{
    gender?: string;
    dateOfBirth?: string;
    weight?: string;
    height?: string;
  }>({});

  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  const tintColor = useThemeColor({}, 'tint');

  // Redirect to login if not authenticated
  useEffect(() => {
    console.log('signup2: isAuthenticated:', isAuthenticated);
    console.log('signup2: user:', user);
    
    if (!isAuthenticated) {
      console.log('signup2: User not authenticated, redirecting to login');
      router.replace('/login');
    } else {
      console.log('signup2: User authenticated, staying on signup2');
    }
  }, [isAuthenticated, user]);

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

  const validateForm = () => {
    const newErrors: typeof errors = {};

    // Gender validation
    if (!gender) {
      newErrors.gender = 'Please select your gender';
    }

    // Date of birth validation
    if (!dobMM || !dobDD || !dobYYYY) {
      newErrors.dateOfBirth = 'Please enter your complete date of birth';
    } else {
      const mm = parseInt(dobMM, 10);
      const dd = parseInt(dobDD, 10);
      const yyyy = parseInt(dobYYYY, 10);
      const currentYear = new Date().getFullYear();

      if (mm < 1 || mm > 12) {
        newErrors.dateOfBirth = 'Month must be between 1 and 12';
      } else if (dd < 1 || dd > 31) {
        newErrors.dateOfBirth = 'Day must be between 1 and 31';
      } else if (yyyy < 1900 || yyyy > currentYear) {
        newErrors.dateOfBirth = `Year must be between 1900 and ${currentYear}`;
      } else {
        // Check if date is valid
        const birthDate = new Date(yyyy, mm - 1, dd);
        if (birthDate.getMonth() !== mm - 1 || birthDate.getDate() !== dd) {
          newErrors.dateOfBirth = 'Please enter a valid date';
        }
      }
    }

    // Weight validation
    if (!weight) {
      newErrors.weight = 'Please enter your weight';
    } else if (parseFloat(weight) <= 0) {
      newErrors.weight = 'Weight must be greater than 0';
    }

    // Height validation
    if (heightUnit === 'ft/in') {
      if (!heightFeet || !heightInches) {
        newErrors.height = 'Please enter both feet and inches';
      } else if (parseInt(heightFeet) < 0 || parseInt(heightInches) < 0 || parseInt(heightInches) >= 12) {
        newErrors.height = 'Please enter valid height values';
      }
    } else {
      if (!height) {
        newErrors.height = 'Please enter your height';
      } else if (parseFloat(height) <= 0) {
        newErrors.height = 'Height must be greater than 0';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      // Convert height to cm
      let heightInCm: number;
      if (heightUnit === 'ft/in') {
        const feet = parseInt(heightFeet, 10) || 0;
        const inches = parseInt(heightInches, 10) || 0;
        heightInCm = Math.round(feet * 30.48 + inches * 2.54);
      } else {
        heightInCm = parseFloat(height);
      }

      // Convert weight to kg
      let weightInKg: number;
      if (weightUnit === 'lbs') {
        weightInKg = parseFloat((parseFloat(weight) * 0.453592).toFixed(1));
      } else {
        weightInKg = parseFloat(weight);
      }

      // Format date as YYYY-MM-DD
      const formattedDate = `${dobYYYY}-${dobMM.padStart(2, '0')}-${dobDD.padStart(2, '0')}`;

      // Update profile via API (user is already authenticated)
      await updateProfile({
        gender,
        date_of_birth: formattedDate,
        weight: weightInKg,
        height: heightInCm,
      });

      // Mark signup flow as complete
      setSignupFlowComplete();

      // Navigate to main app
      router.replace('/(tabs)');
    } catch (error) {
      console.error('Profile update error:', error);
      Alert.alert(
        'Profile Update Failed',
        error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.',
        [{ text: 'OK' }]
      );
    }
  };

  const handleSkip = () => {
    Alert.alert(
      'Skip Profile Setup?',
      'You can always complete your profile later in the settings.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Skip',
          onPress: () => {
            // Mark signup flow as complete
            setSignupFlowComplete();
            // User is already authenticated, just navigate to main app
            router.replace('/(tabs)');
          },
          style: 'destructive'
        }
      ]
    );
  };

  return (
    <KeyboardAvoidingView
      style={[styles.container, { backgroundColor }]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.formContainer}>
          <Text style={[styles.title, { color: textColor }]}>Complete Your Profile</Text>
          <Text style={[styles.subtitle, { color: textColor }]}>
            Help us personalize your fitness experience
          </Text>

          {/* Gender */}
          <Text style={[styles.label, { color: textColor }]}>Gender</Text>
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
          {errors.gender && <Text style={styles.errorText}>{errors.gender}</Text>}

          {/* Date of Birth */}
          <Text style={[styles.label, { color: textColor }]}>Date of Birth</Text>
          <Text style={[styles.subLabel, { color: textColor }]}>MM / DD / YYYY</Text>
          <View style={styles.dobRow}>
            <TextInput
              style={[styles.dobInput, styles.dobPart, { color: textColor }]}
              value={dobMM}
              onChangeText={onChangeDobMM}
              keyboardType="numeric"
              maxLength={2}
              placeholder="MM"
              placeholderTextColor="#aaa"
            />
            <Text style={[styles.slash, { color: textColor }]}>/</Text>
            <TextInput
              ref={ddRef}
              style={[styles.dobInput, styles.dobPart, { color: textColor }]}
              value={dobDD}
              onChangeText={onChangeDobDD}
              keyboardType="numeric"
              maxLength={2}
              placeholder="DD"
              placeholderTextColor="#aaa"
            />
            <Text style={[styles.slash, { color: textColor }]}>/</Text>
            <TextInput
              ref={yyyyRef}
              style={[styles.dobInput, styles.dobYear, { color: textColor }]}
              value={dobYYYY}
              onChangeText={onChangeDobYYYY}
              keyboardType="numeric"
              maxLength={4}
              placeholder="YYYY"
              placeholderTextColor="#aaa"
            />
          </View>
          {errors.dateOfBirth && <Text style={styles.errorText}>{errors.dateOfBirth}</Text>}

          {/* Weight */}
          <Text style={[styles.label, { color: textColor }]}>Weight</Text>
          <View style={styles.row}>
            <TextInput
              style={[styles.textInput, { color: textColor }]}
              value={weight}
              onChangeText={(text) => setWeight(text.replace(/[^0-9.]/g, ''))}
              keyboardType="numeric"
              placeholder="Enter weight"
              placeholderTextColor="#aaa"
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
          {errors.weight && <Text style={styles.errorText}>{errors.weight}</Text>}

          {/* Height */}
          <Text style={[styles.label, { color: textColor }]}>Height</Text>
          <View style={styles.row}>
            {heightUnit === 'ft/in' ? (
              <>
                <TextInput
                  style={[styles.textInput, { color: textColor }]}
                  value={heightFeet}
                  onChangeText={(text) => setHeightFeet(text.replace(/[^0-9]/g, ''))}
                  keyboardType="numeric"
                  placeholder="Feet"
                  placeholderTextColor="#aaa"
                />
                <TextInput
                  style={[styles.textInput, { marginLeft: 10, color: textColor }]}
                  value={heightInches}
                  onChangeText={(text) => setHeightInches(text.replace(/[^0-9]/g, ''))}
                  keyboardType="numeric"
                  placeholder="Inches"
                  placeholderTextColor="#aaa"
                />
              </>
            ) : (
              <TextInput
                style={[styles.textInput, { color: textColor }]}
                value={height}
                onChangeText={(text) => setHeight(text.replace(/[^0-9.]/g, ''))}
                keyboardType="numeric"
                placeholder="Height in cm"
                placeholderTextColor="#aaa"
              />
            )}
            <RNPickerSelect
              onValueChange={(val) => {
                setHeightUnit(val);
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
          {errors.height && <Text style={styles.errorText}>{errors.height}</Text>}

          <Button
            title="Complete Profile"
            onPress={handleNext}
            loading={isLoading}
            loadingText="Saving Profile..."
            fullWidth={true}
            style={styles.completeButton}
          />

          <TouchableOpacity
            onPress={handleSkip}
            style={styles.skipButton}
            accessibilityLabel="Skip profile setup"
            accessibilityRole="button"
            accessible={true}
          >
            <Text style={{ color: tintColor, fontSize: 16 }}>Skip for now</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center',
  },
  formContainer: {
    width: '100%',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 32,
    textAlign: 'center',
    opacity: 0.8,
  },
  label: {
    fontSize: 18,
    marginTop: 16,
    marginBottom: 8,
    fontWeight: '600',
  },
  subLabel: {
    fontSize: 14,
    marginBottom: 8,
    opacity: 0.7,
  },
  dobRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  dobInput: {
    borderWidth: 1,
    borderColor: '#555',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 12,
    borderRadius: 8,
    fontSize: 16,
    textAlign: 'center',
  },
  dobPart: {
    width: 60,
  },
  dobYear: {
    flex: 1,
  },
  slash: {
    fontSize: 18,
    marginHorizontal: 8,
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
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 14,
    marginTop: 4,
    marginBottom: 8,
  },
  completeButton: {
    marginTop: 24,
    marginBottom: 16,
  },
  skipButton: {
    alignItems: 'center',
    padding: 12,
  },
});

const pickerSelectStyles = {
  inputIOS: {
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 8,
    color: 'white',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    paddingRight: 30,
    marginBottom: 8,
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 8,
    color: 'white',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    paddingRight: 30,
    marginBottom: 8,
  },
};

const pickerSelectStylesSmall = {
  inputIOS: {
    fontSize: 16,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 8,
    color: 'white',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
  },
  inputAndroid: {
    fontSize: 16,
    paddingHorizontal: 8,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 8,
    color: 'white',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    paddingRight: 30,
    marginLeft: 10,
    minWidth: 80,
  },
};
