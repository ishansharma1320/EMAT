import React, { useState } from "react";
import { View, Text, TextInput, StyleSheet } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { ValidateUserRegistration } from "../api/api";
import { Button } from "react-native-ui-lib";
function valdateUser({ route }) {
  const [token, setToken] = useState("");
  const { response } = route.params;
  const navigation = useNavigation();

  console.log("This is response//////////////", response);
  const handleValidation = () => {
    ValidateUserRegistration(
      response,
      token,
      (res) => {
        console.log("This is response of updated Expenses", res.data.response);
      },
      (err) => {
        console.log("err", err);
      }
    );
  };

  const handleSubmit = () => {
    ValidateUserRegistration(
      response,
      token,
      (res) => {
        console.log(
          "This is response of updated Expenses",
          res.data.response.verified
        );
        if (res.data.response.verified) {
          navigation.navigate("SignIn");
        } else {
          alert("Enter a valid Token");
        }
      },
      (err) => {
        console.log("err", err);
      }
    );
  };

  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <Text style={styles.passwordRecoveryText}>Enter Validation Token</Text>
      <TextInput
        style={{
          height: 40,
          borderColor: "gray",
          borderWidth: 1,
          width: "80%",
          margin: 10,
          padding: 5,
        }}
        placeholder="Enter your token"
        onChangeText={(text) => setToken(text)}
        value={token}
        keyboardType="text"
      />
      <Button label="Submit" style={styles.button} onPress={handleSubmit} />
    </View>
  );
}
const styles = StyleSheet.create({
  passwordRecoveryText: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
  },
  button: {
    backgroundColor: "blue",
    padding: 12,
    width: "50%",
  },
});

export default valdateUser;
