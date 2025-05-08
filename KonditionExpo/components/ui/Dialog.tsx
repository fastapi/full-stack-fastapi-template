import React from 'react';
import { Modal, View, Text, StyleSheet, TouchableOpacity, TouchableWithoutFeedback, Dimensions } from 'react-native';
import { useThemeColor } from '../../hooks/useThemeColor';

interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  closeOnOverlayClick?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'full';
  footer?: React.ReactNode;
  position?: 'center' | 'bottom';
}

export function Dialog({
  isOpen,
  onClose,
  title,
  children,
  closeOnOverlayClick = true,
  size = 'md',
  footer,
  position = 'center',
}: DialogProps) {
  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  
  // Determine width based on size
  let dialogWidth = 0.9 * Dimensions.get('window').width;
  let maxHeight = 0.8 * Dimensions.get('window').height;
  if (size === 'sm') dialogWidth = 0.7 * Dimensions.get('window').width;
  if (size === 'lg') dialogWidth = 0.95 * Dimensions.get('window').width;
  if (size === 'full') {
    dialogWidth = Dimensions.get('window').width;
    maxHeight = Dimensions.get('window').height;
  }
  
  return (
    <Modal
      visible={isOpen}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback
        onPress={() => {
          if (closeOnOverlayClick) {
            onClose();
          }
        }}
      >
        <View style={styles.overlay}>
          <TouchableWithoutFeedback onPress={(e) => e.stopPropagation()}>
            <View 
              style={[
                styles.dialogContainer, 
                { 
                  backgroundColor,
                  width: dialogWidth, 
                  maxHeight,
                },
                position === 'center' ? styles.centerPosition : styles.bottomPosition
              ]}
            >
              {title && (
                <View style={styles.header}>
                  <Text style={[styles.title, { color: textColor }]}>{title}</Text>
                  
                  <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                    <Text style={{ fontSize: 20, color: textColor }}>×</Text>
                  </TouchableOpacity>
                </View>
              )}
              
              <View style={styles.content}>
                {children}
              </View>
              
              {footer && (
                <View style={styles.footer}>
                  {footer}
                </View>
              )}
            </View>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  dialogContainer: {
    borderRadius: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  centerPosition: {
    alignSelf: 'center',
  },
  bottomPosition: {
    position: 'absolute',
    bottom: 0,
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    alignSelf: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
  },
  closeButton: {
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    padding: 16,
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
}); 