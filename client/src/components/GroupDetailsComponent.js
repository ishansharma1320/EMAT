import { React, useState, useEffect, useLayoutEffect, useContext } from "react";
import { Avatar, Text, View, Button, Card } from "react-native-ui-lib";
import GroupActivitiesList from "./GroupActivitiesList";
import { ActivityIndicator, StyleSheet } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import { useNavigation } from "@react-navigation/native";
import { FAB } from "@rneui/themed";
import { getValueFor } from "../utils/secureStore";
import { GroupStatsApi, UpdatedExpenseList } from "../api/api";
import GroupContext from "../Context/GroupContext";

export const GroupDetailsComponent = ({ route }) => {
  const navigation = useNavigation();
  const { selectedGroup, setExpense } = route.params;

  const [expenses, setExpenses] = useState();
  const [userId, setUserId] = useState();
  const [isLoading, setIsLoading] = useState(true);
  const [mostSpender, setMostSpender] = useState();
  const [leastSpender, setLeastSpender] = useState();
  const { groupState } = useContext(GroupContext);
  const handleAddExpense = () => {
    // navigate to Add Expense page
    navigation.push("AddExpense", {
      groupId: selectedGroup.group_id,
      userId: userId,
    });
  };
  const primaryColor = "#E44343";
  const secondaryColor = "#27AE60";

  const handleSettleUp = () => {
    navigation.push("SettleUp", { groupId: selectedGroup.group_id, userId });
  };
  const handleNotify = () => {
    navigation.push("Notify", { groupId: selectedGroup.group_id, userId });
  };
  const fetchUserIdFromSecureStore = async () => {
    let ownUser = await getValueFor("USER_ID");
    setUserId(ownUser);
  };

  useEffect(() => {
    //TODO: api call for fetching overall expense list here
    fetchUserIdFromSecureStore();
    GroupStatsApi(
      selectedGroup.group_id,
      (response) => {
        if (response.data.status) {
          let mostSpender =
            response.data.response.max.first_name +
            " " +
            response.data.response.max.last_name;
          let leastSpender =
            response.data.response.min.first_name +
            " " +
            response.data.response.min.last_name;
          setMostSpender(mostSpender);
          setLeastSpender(leastSpender);
        }
      }, error => {
        console.log(error);
      })

    UpdatedExpenseList(
      selectedGroup.group_id,
      (res) => {
        let expenseList = res.data.response;
        expenseList.sort((a, b)=>(b.created_at["$date"] - a.created_at["$date"]));
        setExpenses(expenseList);
        setIsLoading(false);
      },
      (err) => {
        console.log("err", err);
      }
    );
  }, [groupState]);

  useLayoutEffect(() => {
    navigation.setOptions({
      headerRight: () => (
        <Icon
          name="settings"
          size={24}
          onPress={() =>
            navigation.push("GroupSettings", { selectedGroup: selectedGroup })
          }
        />
      ),
    });
  });

  if (isLoading) {
    return (
      <View flex center>
        <ActivityIndicator size="large" color="blue" />
      </View>
    );
  }
  return (
    <>
      <View style={styles.container}>
        <View flex row centerV spread>
          <Text style={styles.fontTitle}>{selectedGroup.group_name}</Text>
          <Avatar size={76} source={require("../../assets/group/3.png")} />
        </View>

        <View style={styles.cardContainer}>
          <Card style={[styles.card, { backgroundColor: primaryColor }]}>
            <Text white>Least Spending</Text>
            <Text white style={styles.boldText}>
              {leastSpender}
            </Text>
          </Card>
          <Card style={[styles.card, { backgroundColor: secondaryColor }]}>
            <Text white>Most Spending</Text>
            <Text white style={styles.boldText}>
              {mostSpender}
            </Text>
          </Card>
        </View>

        <View flex row center style={{ justifyContent: "space-around" }}>
          <Button
            label={"Settle Up"}
            style={styles.button}
            onPress={handleSettleUp}
          ></Button>
          <Button
            label={"Notify"}
            style={styles.button}
            onPress={handleNotify}
          ></Button>
        </View>
      </View>
      <View flex center>
        <Text style={styles.fontTitle}>Activities</Text>
        {expenses && expenses.length !== 0 ? (
          <GroupActivitiesList
            groupId={selectedGroup.group_id}
            noOfParticipants={selectedGroup.participants.length}
            userId={userId}
            activities={expenses}
          />
        ) : (
          <Text>No expenses</Text>
        )}
      </View>
      <FAB
        icon={{ name: "money", color: "white" }}
        color="blue"
        placement="right"
        onPress={handleAddExpense}
      />
    </>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#E1E1E1",
    paddingHorizontal: 24,
    borderBottomLeftRadius: 16,
    borderBottomRightRadius: 16,
  },
  detailsContainer: { flexDirection: "row", marginVertical: 16 },
  buttonGroup: { flexDirection: "row", justifyContent: "center" },
  fontTitle: { fontWeight: "bold", fontSize: 24, marginVertical: 12 },
  cardContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  card: {
    width: "47%",
    height: 80,
    borderRadius: 10,
    justifyContent: "center",
    alignItems: "center",
  },
  boldText: {
    fontWeight: "bold",
  },
  button: {
    backgroundColor: "blue",
    padding: 12,
    width: "40%",
  },
});
