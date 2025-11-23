import React, { useState } from "react";
import { View, TextInput, StyleSheet, ViewStyle, TextStyle} from "react-native";
import { SendButton, RecordButton } from "./ChatButton";
import { sizes } from "../themes/sizes";
import { spacing } from "../themes/spacing";
import { colors } from "../themes/colors";

interface ChatInputProps {
    onSend: (text: string) => void;
    onRecordStart: () => void;
    onRecordStop: () => void;
    disabled?: boolean;
    submitOnEnter?: boolean;
    style?: ViewStyle | ViewStyle[];
    textStyle?: TextStyle | TextStyle[];
}

export function ChatInput({
    onSend,
    onRecordStart,
    onRecordStop,
    disabled = false,
    submitOnEnter = false,
    style
}: ChatInputProps) {
    const [text, setText] = useState("");

    const handleSubmit = () => {
        if (text.trim().length === 0) return;
        onSend(text);
        setText("");
    };

    return (
        <View style={[styles.container, style]}>
            <TextInput
                style={styles.textInput}
                value={text}
                onChangeText={setText}
                placeholder="Message..."
                onSubmitEditing={() => submitOnEnter && handleSubmit()}
            />

            <SendButton
                onPress={handleSubmit}
                disabled={disabled || text.length == 0}
            >
                {/* for now the icon will be outside component */}
            </SendButton>

            <RecordButton
                onPressIn={onRecordStart}
                onPressOut={onRecordStop}
                disabled={disabled}
            >
                {/* for now the icon will be outside component */}
            </RecordButton>
        </View>
    )
}


const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderTopWidth: 1,
    borderColor: "#CCC", // move to theme later
    backgroundColor: "white",
    alignItems: "center",
  },
  textInput: {
    flex: 1,
    height: 40,
    borderColor: "#DDD",
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: spacing.md,
  },
});