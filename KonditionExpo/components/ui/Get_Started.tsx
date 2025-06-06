import { useStyles, createStyleSheet } from 'styles';
import { View, Text } from 'react-native';

export interface Component1Props {
  /** Used to locate this view in end-to-end tests. */
  testID?: string;
}

export function Component1(props: Component1Props) {
  const styles = useStyles(stylesheet);

  return (
    <View style={styles.root} testID={props.testID ?? "119:1799"}>
      <View style={styles.rectangle5853} testID="76:782" />
      <Text style={styles.getStarted} testID="76:783">
        Get Started
      </Text>
    </View>
  );
}

const stylesheet = createStyleSheet((theme) => ({
  root: {
    width: 315,
    height: 60,
    flexShrink: 0,
  },
  rectangle5853: {
    width: 315,
    height: 60,
    flexShrink: 0,
    borderBottomLeftRadius: 99,
    borderBottomRightRadius: 99,
    borderTopLeftRadius: 99,
    borderTopRightRadius: 99,
    backgroundColor: theme.colors.white, // Example usage
    shadowColor: "rgba(0, 0, 0, 0.25)",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 1,
    shadowRadius: 4,
    elevation: 4, // For Android
  },
  getStarted: {
    fontFamily: 'Poppins',
    fontSize: 16,
    fontStyle: 'normal',
    fontWeight: '700',
    backgroundColor: theme.colors.blue, // Example usage
  },
}));
