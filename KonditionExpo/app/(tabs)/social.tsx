import React, { useState, useEffect, useCallback } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useSocial } from '@/contexts/SocialContext';
import { SearchBar } from '@/components/social/SearchBar';
import { UserList } from '@/components/social/UserList';
import { UserSearchResult, UserProfile } from '@/services/api';

type ConnectionsTab = 'following' | 'followers';

const SocialScreen = () => {
  const {
    searchResults,
    searchLoading,
    searchError,
    followers,
    following,
    followersLoading,
    followingLoading,
    followersError,
    followingError,
    searchUsers,
    clearSearchResults,
    getFollowers,
    getFollowing,
    refreshFollowers,
    refreshFollowing,
  } = useSocial();

  const [activeTab, setActiveTab] = useState<ConnectionsTab>('following');
  const [refreshing, setRefreshing] = useState(false);
  const [showSearch, setShowSearch] = useState(true);

  useEffect(() => {
    // Load initial data
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      await Promise.all([
        getFollowing(0, 100),
        getFollowers(0, 100),
      ]);
    } catch (error) {
      console.error('Failed to load connections:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      if (showSearch && searchResults.length > 0) {
        // If we're showing search results, don't refresh connections
        setRefreshing(false);
        return;
      }
      
      if (activeTab === 'following') {
        await refreshFollowing();
      } else {
        await refreshFollowers();
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  const handleSearch = useCallback(async (query: string) => {
    setShowSearch(true);
    await searchUsers(query);
  }, [searchUsers]);

  const handleClearSearch = useCallback(() => {
    clearSearchResults();
    setShowSearch(false);
  }, [clearSearchResults]);

  const handleUserPress = (user: UserSearchResult | UserProfile) => {
    // TODO: Navigate to user profile screen
    Alert.alert('User Profile', `View profile for ${user.full_name || user.email}`);
  };

  const renderTabButton = (tab: ConnectionsTab, label: string, count: number) => (
    <TouchableOpacity
      style={[
        styles.tabButton,
        activeTab === tab && styles.activeTabButton,
      ]}
      onPress={() => setActiveTab(tab)}
    >
      <Text style={[
        styles.tabButtonText,
        activeTab === tab && styles.activeTabButtonText,
      ]}>
        {label}
      </Text>
      <Text style={[
        styles.tabCount,
        activeTab === tab && styles.activeTabCount,
      ]}>
        {count}
      </Text>
    </TouchableOpacity>
  );

  const renderSearchSection = () => (
    <View style={styles.searchSection}>
      <SearchBar
        onSearch={handleSearch}
        onClear={handleClearSearch}
        loading={searchLoading}
        placeholder="Search for users..."
      />
      
      {searchError && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={20} color="#FF6B6B" />
          <Text style={styles.errorText}>{searchError}</Text>
        </View>
      )}
      
      {showSearch && (
        <View style={styles.searchResults}>
          <Text style={styles.sectionTitle}>
            Search Results ({searchResults.length})
          </Text>
          <UserList
            users={searchResults}
            loading={searchLoading}
            onUserPress={handleUserPress}
            emptyTitle="No Users Found"
            emptyMessage="Try searching with different keywords."
            size="normal"
            context="search"
          />
        </View>
      )}
    </View>
  );

  const renderConnectionsSection = () => {
    if (showSearch && searchResults.length > 0) {
      return null;
    }

    const currentUsers = activeTab === 'following' ? following : followers;
    const currentLoading = activeTab === 'following' ? followingLoading : followersLoading;
    const currentError = activeTab === 'following' ? followingError : followersError;
    
    // Debug logging
    console.log(`[Social] Active tab: ${activeTab}, Users count: ${currentUsers.length}`);
    if (activeTab === 'following' && currentUsers.length > 0) {
      console.log(`[Social] Following users:`, currentUsers.map(u => ({
        name: u.full_name || u.email,
        is_following: 'is_following' in u ? u.is_following : 'N/A'
      })));
    }

    return (
      <View style={styles.connectionsSection}>
        <Text style={styles.sectionTitle}>My Connections</Text>
        
        <View style={styles.tabContainer}>
          {renderTabButton('following', 'Following', following.length)}
          {renderTabButton('followers', 'Followers', followers.length)}
        </View>
        
        {currentError && (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={20} color="#FF6B6B" />
            <Text style={styles.errorText}>{currentError}</Text>
          </View>
        )}
        
        <UserList
          users={currentUsers}
          loading={currentLoading}
          refreshing={refreshing}
          onRefresh={handleRefresh}
          onUserPress={handleUserPress}
          showFollowButton={true}
          emptyTitle={activeTab === 'following' ? "Not Following Anyone" : "No Followers"}
          emptyMessage={
            activeTab === 'following'
              ? "Start following users to see them here."
              : "Other users will appear here when they follow you."
          }
          size="normal"
          context={activeTab}
        />
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Social</Text>
        <Text style={styles.headerSubtitle}>
          Connect with other fitness enthusiasts
        </Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#70A1FF']}
            tintColor="#70A1FF"
          />
        }
      >
        {renderSearchSection()}
        {renderConnectionsSection()}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    padding: 20,
    backgroundColor: '#F8F9FA',
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#666',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 80,
  },
  searchSection: {
    backgroundColor: '#FFFFFF',
  },
  searchResults: {
    marginTop: 8,
  },
  connectionsSection: {
    marginTop: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
    marginHorizontal: 16,
    marginBottom: 12,
  },
  tabContainer: {
    flexDirection: 'row',
    marginHorizontal: 16,
    marginBottom: 16,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: 4,
  },
  tabButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  activeTabButton: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  tabButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#666',
    marginRight: 6,
  },
  activeTabButtonText: {
    color: '#70A1FF',
    fontWeight: '600',
  },
  tabCount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#999',
    backgroundColor: '#F0F0F0',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 10,
    minWidth: 20,
    textAlign: 'center',
  },
  activeTabCount: {
    color: '#70A1FF',
    backgroundColor: '#E8F0FF',
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
    marginVertical: 8,
    padding: 12,
    backgroundColor: '#FFF5F5',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FED7D7',
  },
  errorText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#E53E3E',
    flex: 1,
  },
});

export default SocialScreen;