import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  Switch,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { router } from 'expo-router';
import { useFeed } from '../contexts/FeedContext';
import { WorkoutPostCreateRequest } from '../services/api';
import { IconSymbol } from '../components/ui/IconSymbol';

const WORKOUT_TYPES = [
  'Running',
  'Cycling',
  'Swimming',
  'Strength Training',
  'Yoga',
  'Pilates',
  'CrossFit',
  'Boxing',
  'Dancing',
  'Walking',
  'Hiking',
  'Other',
];

export default function CreatePostScreen() {
  const { createPost, isLoading } = useFeed();
  
  const [formData, setFormData] = useState<WorkoutPostCreateRequest>({
    title: '',
    description: '',
    workout_type: 'Running',
    duration_minutes: 30,
    calories_burned: undefined,
    is_public: true,
  });

  const [showWorkoutTypes, setShowWorkoutTypes] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    // Prevent multiple submissions
    if (isSubmitting || isLoading) {
      return;
    }

    // Validation
    if (!formData.title.trim()) {
      Alert.alert('Error', 'Please enter a title for your workout');
      return;
    }

    if (formData.duration_minutes <= 0) {
      Alert.alert('Error', 'Duration must be greater than 0');
      return;
    }

    setIsSubmitting(true);

    try {
      await createPost(formData);
      
      // Success - navigate back immediately
      setIsSubmitting(false);
      
      // Show a brief success message and navigate back
      Alert.alert(
        'Success',
        'Your workout post has been created!',
        [
          {
            text: 'OK',
            onPress: () => router.back()
          }
        ]
      );
      
      // Fallback: navigate back after a short delay if alert doesn't work
      setTimeout(() => {
        router.back();
      }, 2000);
      
    } catch (error) {
      setIsSubmitting(false);
      console.error('Error creating post:', error);
      Alert.alert('Error', 'Failed to create post. Please try again.');
    }
  };

  const handleCancel = () => {
    router.back();
  };

  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleCancel} style={styles.headerButton}>
          <Text style={styles.cancelText}>Cancel</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Create Post</Text>
        <TouchableOpacity
          onPress={handleSubmit}
          style={[
            styles.headerButton,
            styles.postButton,
            (isLoading || isSubmitting) && { opacity: 0.6 }
          ]}
          disabled={isLoading || isSubmitting}
        >
          <Text style={[styles.postText, (isLoading || isSubmitting) && styles.disabledText]}>
            {(isLoading || isSubmitting) ? 'Posting...' : 'Post'}
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Title */}
        <View style={styles.section}>
          <Text style={styles.label}>Title *</Text>
          <TextInput
            style={styles.textInput}
            value={formData.title}
            onChangeText={(text) => setFormData(prev => ({ ...prev, title: text }))}
            placeholder="What did you do today?"
            maxLength={255}
          />
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={styles.label}>Description</Text>
          <TextInput
            style={[styles.textInput, styles.textArea]}
            value={formData.description}
            onChangeText={(text) => setFormData(prev => ({ ...prev, description: text }))}
            placeholder="Tell us about your workout..."
            multiline
            numberOfLines={4}
            maxLength={1000}
          />
        </View>

        {/* Workout Type */}
        <View style={styles.section}>
          <Text style={styles.label}>Workout Type *</Text>
          <TouchableOpacity
            style={styles.dropdown}
            onPress={() => setShowWorkoutTypes(!showWorkoutTypes)}
          >
            <Text style={styles.dropdownText}>{formData.workout_type}</Text>
            <IconSymbol 
              name={showWorkoutTypes ? "chevron.up" : "chevron.down"} 
              size={16} 
              color="#666" 
            />
          </TouchableOpacity>
          
          {showWorkoutTypes && (
            <View style={styles.dropdownOptions}>
              {WORKOUT_TYPES.map((type) => (
                <TouchableOpacity
                  key={type}
                  style={styles.dropdownOption}
                  onPress={() => {
                    setFormData(prev => ({ ...prev, workout_type: type }));
                    setShowWorkoutTypes(false);
                  }}
                >
                  <Text style={[
                    styles.dropdownOptionText,
                    formData.workout_type === type && styles.selectedOption
                  ]}>
                    {type}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>

        {/* Duration */}
        <View style={styles.section}>
          <Text style={styles.label}>Duration (minutes) *</Text>
          <View style={styles.durationContainer}>
            <TextInput
              style={styles.numberInput}
              value={formData.duration_minutes.toString()}
              onChangeText={(text) => {
                const minutes = parseInt(text) || 0;
                setFormData(prev => ({ ...prev, duration_minutes: minutes }));
              }}
              keyboardType="numeric"
              placeholder="30"
            />
            <Text style={styles.durationDisplay}>
              = {formatDuration(formData.duration_minutes)}
            </Text>
          </View>
        </View>

        {/* Calories */}
        <View style={styles.section}>
          <Text style={styles.label}>Calories Burned</Text>
          <TextInput
            style={styles.numberInput}
            value={formData.calories_burned?.toString() || ''}
            onChangeText={(text) => {
              const calories = text ? parseInt(text) || undefined : undefined;
              setFormData(prev => ({ ...prev, calories_burned: calories }));
            }}
            keyboardType="numeric"
            placeholder="Optional"
          />
        </View>

        {/* Privacy Setting */}
        <View style={styles.section}>
          <View style={styles.privacyContainer}>
            <View style={styles.privacyInfo}>
              <Text style={styles.label}>Privacy Setting</Text>
              <Text style={styles.privacyDescription}>
                {formData.is_public 
                  ? "Public - Visible to everyone" 
                  : "Private - Only visible to mutual followers"
                }
              </Text>
            </View>
            <Switch
              value={formData.is_public}
              onValueChange={(value) => setFormData(prev => ({ ...prev, is_public: value }))}
              trackColor={{ false: '#FF9800', true: '#4CAF50' }}
              thumbColor="#fff"
            />
          </View>
          
          <View style={styles.privacyIndicator}>
            <IconSymbol 
              name={formData.is_public ? "globe" : "lock.fill"} 
              size={16} 
              color={formData.is_public ? "#4CAF50" : "#FF9800"} 
            />
            <Text style={[styles.privacyText, { color: formData.is_public ? "#4CAF50" : "#FF9800" }]}>
              {formData.is_public ? "Public Post" : "Private Post"}
            </Text>
          </View>
        </View>

        {/* Preview */}
        <View style={styles.section}>
          <Text style={styles.label}>Preview</Text>
          <View style={styles.preview}>
            <Text style={styles.previewTitle}>{formData.title || 'Your workout title'}</Text>
            {formData.description && (
              <Text style={styles.previewDescription}>{formData.description}</Text>
            )}
            <View style={styles.previewStats}>
              <Text style={styles.previewStat}>
                🏃‍♂️ {formData.workout_type}
              </Text>
              <Text style={styles.previewStat}>
                ⏱️ {formatDuration(formData.duration_minutes)}
              </Text>
              {formData.calories_burned && (
                <Text style={styles.previewStat}>
                  🔥 {formData.calories_burned} cal
                </Text>
              )}
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
    paddingTop: 50, // Account for status bar
  },
  headerButton: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  postButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  cancelText: {
    fontSize: 16,
    color: '#666',
  },
  postText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  disabledText: {
    opacity: 0.6,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  dropdown: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    backgroundColor: '#f9f9f9',
  },
  dropdownText: {
    fontSize: 16,
    color: '#333',
  },
  dropdownOptions: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    backgroundColor: '#fff',
    marginTop: 4,
    maxHeight: 200,
  },
  dropdownOption: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  dropdownOptionText: {
    fontSize: 16,
    color: '#333',
  },
  selectedOption: {
    color: '#007AFF',
    fontWeight: '600',
  },
  durationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  numberInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
    width: 100,
    marginRight: 12,
  },
  durationDisplay: {
    fontSize: 16,
    color: '#666',
  },
  privacyContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  privacyInfo: {
    flex: 1,
  },
  privacyDescription: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  privacyIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  privacyText: {
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 6,
  },
  preview: {
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 16,
  },
  previewTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#333',
    marginBottom: 8,
  },
  previewDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  previewStats: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  previewStat: {
    fontSize: 14,
    color: '#666',
  },
});