import { TouchableOpacity, StyleSheet, TouchableOpacityProps, ViewStyle } from "react-native";
import { sizes } from "../themes/sizes";
import { spacing } from "../themes/spacing";

interface ChatButtonProps extends TouchableOpacityProps {
    style?: ViewStyle | ViewStyle[];
    children: React.ReactNode;
}

export function SendButton({children, style, ...props}: ChatButtonProps) {
    return (
        <TouchableOpacity style= {[styles.base, style]} {...props}>
            {children}
        </TouchableOpacity>
    );
}

export function RecordButton({ children, style, ...props}: ChatButtonProps) {
    return (
        <TouchableOpacity style={[styles.base, style]} {...props}>
            {children}
        </TouchableOpacity>
    )
}

const styles = StyleSheet.create({
    base: {
        width: sizes.iconButton,
        height: sizes.iconButton,
        justifyContent: "center",
        alignItems: "center",
        marginLeft: spacing.sm,  
    },
})