import { View, Text, StyleSheet, ViewStyle, TextStyle } from "react-native";
import { colors } from "../themes/colors";
import { spacing } from "../themes/spacing";

interface ChatBubbleProps {
    role?: "user" | "assistant" | string;
    children: React.ReactNode;
    style?: ViewStyle | ViewStyle[];
    textStyle?: TextStyle | TextStyle[];
}

export function ChatBubble({ 
    role = "assistant", children, textStyle, style}: ChatBubbleProps) {
        const isUser = role === "user";

        return (
            <View
             style = {[
                styles.base,
                isUser ? styles.user : styles.assistant,
                style
            ]}
            >
                <Text
                 style = {[
                    styles.textBase,
                    isUser ? styles.userText : styles.assistantText,
                    textStyle
                 ]}
                 >
                    {children}
                </Text>
            </View>
        );
    }

    const styles = StyleSheet.create({
        base: {
            padding: spacing.md,
            borderRadius: 18,
            marginBottom: spacing.md,
            maxWidth: "80%",
        },
        user: {
            backgroundColor: colors.userBubbleBg,
            alignSelf: "flex-end",
            borderBottomRightRadius: 2,
        },
        assistant: {
            backgroundColor: colors.assistantBubbleBg,
            alignSelf: "flex-start",
            borderBottomLeftRadius: 2,
        },
        textBase: {
            fontSize: 16,
        },
        userText: {
            color: colors.textLight,
        },
        assistantText: {
            color: colors.textDark,
        },
    });