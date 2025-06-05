import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { FeedType } from '../../contexts/FeedContext';

interface FeedToggleProps {
  currentFeedType: FeedType;
  onFeedTypeChange: (feedType: FeedType) => void;
  postCounts?: {
    personal: number;
    public: number;
    combined: number;
  };
}

export function FeedToggle({ currentFeedType, onFeedTypeChange, postCounts }: FeedToggleProps) {
  const feedOptions: { type: FeedType; label: string; description: string }[] = [
    { type: 'personal', label: 'Personal', description: 'Following' },
    { type: 'public', label: 'Public', description: 'Discover' },
    { type: 'combined', label: 'Combined', description: 'Mixed' },
  ];

  return (
    <View style={styles.container}>
      {feedOptions.map((option) => {
        const isActive = currentFeedType === option.type;
        const count = postCounts?.[option.type] || 0;
        
        return (
          <TouchableOpacity
            key={option.type}
            style={[styles.tab, isActive && styles.activeTab]}
            onPress={() => onFeedTypeChange(option.type)}
            activeOpacity={0.7}
          >
            <Text style={[styles.tabLabel, isActive && styles.activeTabLabel]}>
              {option.label}
            </Text>
            <Text style={[styles.tabDescription, isActive && styles.activeTabDescription]}>
              {option.description}
            </Text>
            {count > 0 && (
              <View style={[styles.badge, isActive && styles.activeBadge]}>
                <Text style={[styles.badgeText, isActive && styles.activeBadgeText]}>
                  {count > 99 ? '99+' : count}
                </Text>
              </View>
            )}
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 4,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 8,
    alignItems: 'center',
    position: 'relative',
  },
  activeTab: {
    backgroundColor: '#007AFF',
    shadowColor: '#007AFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  tabLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 2,
  },
  activeTabLabel: {
    color: '#fff',
  },
  tabDescription: {
    fontSize: 11,
    color: '#999',
  },
  activeTabDescription: {
    color: '#E3F2FD',
  },
  badge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#FF3B30',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 6,
  },
  activeBadge: {
    backgroundColor: '#fff',
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#fff',
  },
  activeBadgeText: {
    color: '#007AFF',
  },
});