import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  Text,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface SearchBarProps {
  onSearch: (query: string) => void;
  onClear: () => void;
  placeholder?: string;
  debounceMs?: number;
  loading?: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  onClear,
  placeholder = "Search users...",
  debounceMs = 300,
  loading = false,
}) => {
  const [query, setQuery] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // Clear previous timeout
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new timeout for debounced search
    if (query.trim()) {
      debounceRef.current = setTimeout(() => {
        onSearch(query.trim());
      }, debounceMs);
    } else {
      // Clear results immediately when query is empty
      onClear();
    }

    // Cleanup timeout on unmount
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [query, debounceMs]); // Removed onSearch and onClear from dependencies

  const handleClear = () => {
    setQuery('');
    onClear();
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Ionicons 
          name="search" 
          size={20} 
          color="#999" 
          style={styles.searchIcon} 
        />
        <TextInput
          style={styles.input}
          value={query}
          onChangeText={setQuery}
          placeholder={placeholder}
          placeholderTextColor="#999"
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="search"
          clearButtonMode="never" // We'll handle clear manually
        />
        {query.length > 0 && (
          <TouchableOpacity
            onPress={handleClear}
            style={styles.clearButton}
            disabled={loading}
          >
            {loading ? (
              <Ionicons name="refresh" size={20} color="#999" />
            ) : (
              <Ionicons name="close-circle" size={20} color="#999" />
            )}
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#E9ECEF',
  },
  searchIcon: {
    marginRight: 8,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    paddingVertical: 4,
  },
  clearButton: {
    padding: 4,
    marginLeft: 8,
  },
});