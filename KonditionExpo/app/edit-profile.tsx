import React, { useState, useEffect } from 'react';
import { SafeAreaView, View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert, Platform } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { router } from 'expo-router';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import DateTimePicker from '@react-native-community/datetimepicker';

const EditProfileScreen = () => {
  const { user, updateProfile, isLoading } = useAuth();
  const [isUpdating, setIsUpdating] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  
  // Form state
  const [fullName, setFullName] = useState('');
  const [heightFeet, setHeightFeet] = useState('');
  const [heightInches, setHeightInches] = useState('');
  const [weightLbs, setWeightLbs] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState<Date>(new Date());
  const [gender, setGender] = useState('');
  
  // Validation errors
  const [nameError, setNameError] = useState('');
  const [heightError, setHeightError] = useState('');
  const [weightError, setWeightError] = useState('');
  const [dobError, setDobError] = useState('');

  // Unit conversion functions
  const cmToFeetInches = (cm: number): { feet: number; inches: number } => {
    const totalInches = cm / 2.54;
    const feet = Math.floor(totalInches / 12);
    const inches = Math.round(totalInches % 12);
    return { feet, inches };
  };

  const feetInchesToCm = (feet: number, inches: number): number => {
    return Math.round((feet * 12 + inches) * 2.54);
  };

  const kgToLbs = (kg: number): number => {
    return Math.round(kg * 2.20462);
  };

  const lbsToKg = (lbs: number): number => {
    return Math.round(lbs / 2.20462 * 100) / 100;
  };

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setGender(user.gender || '');
      
      if (user.height) {
        const { feet, inches } = cmToFeetInches(user.height);
        setHeightFeet(feet.toString());
        setHeightInches(inches.toString());
      }
      
      if (user.weight) {
        setWeightLbs(kgToLbs(user.weight).toString());
      }
      
      if (user.date_of_birth) {
        setDateOfBirth(new Date(user.date_of_birth));
      }
    }
  }, [user]);

  // Validation functions
  const validateName = (name: string): boolean => {
    if (name.trim().length < 2) {
      setNameError('Name must be at least 2 characters');
      return false;
    }
    setNameError('');
    return true;
  };

  const validateHeight = (feet: string, inches: string): boolean => {
    if (!feet && !inches) {
      setHeightError('');
      return true; // Optional field
    }
    
    const feetNum = parseInt(feet);
    const inchesNum = parseInt(inches);
    
    if (isNaN(feetNum) || isNaN(inchesNum)) {
      setHeightError('Please enter valid numbers');
      return false;
    }
    
    if (feetNum < 3 || feetNum > 8) {
      setHeightError('Height must be between 3 and 8 feet');
      return false;
    }
    
    if (inchesNum < 0 || inchesNum >= 12) {
      setHeightError('Inches must be between 0 and 11');
      return false;
    }
    
    setHeightError('');
    return true;
  };

  const validateWeight = (weight: string): boolean => {
    if (!weight) {
      setWeightError('');
      return true; // Optional field
    }
    
    const weightNum = parseFloat(weight);
    
    if (isNaN(weightNum)) {
      setWeightError('Please enter a valid number');
      return false;
    }
    
    if (weightNum < 50 || weightNum > 1000) {
      setWeightError('Weight must be between 50 and 1000 lbs');
      return false;
    }
    
    setWeightError('');
    return true;
  };

  const validateDateOfBirth = (date: Date): boolean => {
    const today = new Date();
    const minDate = new Date(today.getFullYear() - 120, today.getMonth(), today.getDate());
    const maxDate = new Date(today.getFullYear() - 13, today.getMonth(), today.getDate());
    
    if (date < minDate || date > maxDate) {
      setDobError('Age must be between 13 and 120 years');
      return false;
    }
    
    setDobError('');
    return true;
  };

  // Save profile
  const handleSaveProfile = async () => {
    // Validate all fields
    const isNameValid = validateName(fullName);
    const isHeightValid = validateHeight(heightFeet, heightInches);
    const isWeightValid = validateWeight(weightLbs);
    const isDobValid = validateDateOfBirth(dateOfBirth);
    
    if (!isNameValid || !isHeightValid || !isWeightValid || !isDobValid) {
      return;
    }
    
    try {
      setIsUpdating(true);
      
      const updateData: any = {
        full_name: fullName.trim(),
        gender: gender || undefined,
      };
      
      // Add height if provided
      if (heightFeet && heightInches) {
        updateData.height = feetInchesToCm(parseInt(heightFeet), parseInt(heightInches));
      }
      
      // Add weight if provided
      if (weightLbs) {
        updateData.weight = lbsToKg(parseFloat(weightLbs));
      }
      
      // Add date of birth
      updateData.date_of_birth = dateOfBirth.toISOString().split('T')[0];
      
      await updateProfile(updateData);
      
      Alert.alert('Success', 'Profile updated successfully!', [
        { text: 'OK', onPress: () => router.replace('/(tabs)/profile') }
      ]);
    } catch (error) {
      Alert.alert('Error', 'Failed to update profile. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  // Date picker handler
  const onDateChange = (event: any, selectedDate?: Date) => {
    if (Platform.OS === 'android') {
      setShowDatePicker(false);
    }
    
    if (selectedDate) {
      setDateOfBirth(selectedDate);
      validateDateOfBirth(selectedDate);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.replace('/(tabs)/profile')} style={styles.backButton}>
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Edit Profile</Text>
        </View>

        {/* Form */}
        <View style={styles.form}>
          {/* Full Name */}
          <Input
            label="Full Name"
            value={fullName}
            onChangeText={setFullName}
            placeholder="Enter your full name"
            error={nameError}
            isRequired
            autoCapitalize="words"
          />

          {/* Gender */}
          <View style={styles.genderContainer}>
            <Text style={styles.label}>Gender</Text>
            <View style={styles.genderButtons}>
              {['Male', 'Female', 'Other'].map((option) => (
                <TouchableOpacity
                  key={option}
                  style={[
                    styles.genderButton,
                    gender === option.toLowerCase() && styles.genderButtonSelected
                  ]}
                  onPress={() => setGender(option.toLowerCase())}
                >
                  <Text style={[
                    styles.genderButtonText,
                    gender === option.toLowerCase() && styles.genderButtonTextSelected
                  ]}>
                    {option}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Height */}
          <View style={styles.heightContainer}>
            <Text style={styles.label}>Height</Text>
            <View style={styles.heightInputRow}>
              <View style={styles.heightInputGroup}>
                <Input
                  value={heightFeet}
                  onChangeText={setHeightFeet}
                  placeholder="5"
                  keyboardType="numeric"
                  style={styles.heightInput}
                />
                <Text style={styles.heightLabel}>feet</Text>
              </View>
              <View style={styles.heightInputGroup}>
                <Input
                  value={heightInches}
                  onChangeText={setHeightInches}
                  placeholder="10"
                  keyboardType="numeric"
                  style={styles.heightInput}
                />
                <Text style={styles.heightLabel}>inches</Text>
              </View>
            </View>
            {heightError ? <Text style={styles.errorText}>{heightError}</Text> : null}
          </View>

          {/* Weight */}
          <View style={styles.weightContainer}>
            <Input
              label="Weight (lbs)"
              value={weightLbs}
              onChangeText={setWeightLbs}
              placeholder="150"
              keyboardType="numeric"
              error={weightError}
            />
          </View>

          {/* Date of Birth */}
          <View style={styles.dobContainer}>
            <Text style={styles.label}>Date of Birth</Text>
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowDatePicker(true)}
            >
              <Text style={styles.dateButtonText}>
                {dateOfBirth.toLocaleDateString()}
              </Text>
            </TouchableOpacity>
            {dobError ? <Text style={styles.errorText}>{dobError}</Text> : null}
          </View>

          {/* Save Button */}
          <Button
            title={isUpdating ? 'Saving...' : 'Save Changes'}
            onPress={handleSaveProfile}
            loading={isUpdating}
            style={styles.saveButton}
          />
        </View>
      </ScrollView>

      {/* Date Picker */}
      {showDatePicker && (
        <DateTimePicker
          value={dateOfBirth}
          mode="date"
          display={Platform.OS === 'ios' ? 'spinner' : 'default'}
          onChange={onDateChange}
          maximumDate={new Date(new Date().getFullYear() - 13, new Date().getMonth(), new Date().getDate())}
          minimumDate={new Date(new Date().getFullYear() - 120, new Date().getMonth(), new Date().getDate())}
        />
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    padding: 16,
    paddingBottom: 80,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  backButton: {
    marginRight: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#70A1FF',
    fontWeight: '500',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  form: {
    flex: 1,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  genderContainer: {
    marginBottom: 24,
  },
  genderButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  genderButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  genderButtonSelected: {
    backgroundColor: '#70A1FF',
    borderColor: '#70A1FF',
  },
  genderButtonText: {
    fontSize: 14,
    color: '#555',
    fontWeight: '500',
  },
  genderButtonTextSelected: {
    color: '#FFF',
  },
  heightContainer: {
    marginBottom: 24,
  },
  heightInputRow: {
    flexDirection: 'row',
    gap: 16,
  },
  heightInputGroup: {
    flex: 1,
    alignItems: 'center',
  },
  heightInput: {
    marginBottom: 8,
  },
  heightLabel: {
    fontSize: 14,
    color: '#555',
  },
  weightContainer: {
    marginBottom: 24,
  },
  dobContainer: {
    marginBottom: 32,
  },
  dateButton: {
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: 6,
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#FFF',
  },
  dateButtonText: {
    fontSize: 16,
    color: '#333',
  },
  errorText: {
    fontSize: 12,
    color: '#E53E3E',
    marginTop: 4,
  },
  saveButton: {
    backgroundColor: '#70A1FF',
    marginTop: 16,
  },
});

export default EditProfileScreen;