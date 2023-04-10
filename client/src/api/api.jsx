import instance from './axios'

const CreateUser = async (data, onSuccess, onError) => {
  try {

    const res = await instance.post("/auth/register", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};
const LoginUser = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("/auth/login", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}
const UpdateUser = async (data, onSuccess, onError) => {
  try {
    const res = await instance.put("/profie/update", data, {
      headers: {
        "Content-Type": "application/json"
      },
    })
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const FetchGroups = async (onSuccess, onError) => {
  try {
    const res = await instance.get("/group/list", {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const RegisterGroup = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("/group/register", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const FetchCurrencyList = async (onSuccess, onError) => {
  try {
    const res = await instance.get("/currency/list", {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const FetchDetailedCurrencyList = async (onSuccess, onError) => {
  try {
    const res = await instance.get("/currency/details", {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}
const UserDetails = async (onSuccess, onError) => {
  try {
    const res = await instance.get("/profile/user", {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const FetchActivitiesList = async (onSuccess, onError) => {
  try {
    const res = await instance.get("/activities/list", {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}
const FetchOtherUserProfile = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("/profile/other_user_details", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const FetchProfileEmail = async (onSuccess, onError) => {
  try {
    const res = await instance.get("/profile/email", {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};


const JoinGroupApi = async (verification_code, onSuccess, onError) => {
  try {
    const res = await instance.get(`/group/join-group?verification_code=${verification_code}`, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}
const OverallGroupStandings = async (groupId, onSuccess, onError) => {
  try {
    const res = await instance.get(`${"/settleUp?group_id=" + groupId}`, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);

  } catch (err) {

    onError && onError(err);

  }

};


const CreateExpense = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("/expense/create", data, {
      headers: { "Content-Type": "application/json" },
    });

    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};
const GroupStatsApi = async (group_id, onSuccess, onError) => {
  try {
    const res = await instance.get(`/group/stats?group_id=${group_id}`, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}
const UpdatedExpenseList = async (group_id, onSuccess, onError) => {
  try {
    const res = await instance.get(`/expense/list?group_id=${group_id}`, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

const ValidateUserRegistration = async (UID, vc, onSuccess, onError) => {
  try {
    const res = await instance.get(`/auth/verify-user?user_id=${UID}&verification_code=${vc}`, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}


const SettleUpExpenses = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("/settleUp/settle", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};

const NotifyUsers = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("/settleUp/notify", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};

const UpdateExpenseInfo = async (data, onSuccess, onError) => {
  try {
    const res = await instance.put("/expense/update", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};
const ForgotPassword = async (data, onSuccess, onError) => {
  try {
    const res = await instance.post("auth/reset", data, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
};
const UpdatePassword = async (token, password, onSuccess, onError) => {
  try {
    const res = await instance.post(`/auth/reset/${token}`, password, {
      headers: { "Content-Type": "application/json" },
    });
    onSuccess && onSuccess(res);
  } catch (err) {
    onError && onError(err);
  }
}

export {
  ForgotPassword,
  UpdatePassword,
  CreateUser,
  LoginUser,
  FetchGroups,
  RegisterGroup,
  FetchCurrencyList,
  FetchDetailedCurrencyList,
  UpdateUser,
  FetchActivitiesList,
  FetchOtherUserProfile,
  UserDetails,
  FetchProfileEmail,
  OverallGroupStandings,
  CreateExpense,
  SettleUpExpenses,
  NotifyUsers,
  JoinGroupApi,
  GroupStatsApi,
  UpdatedExpenseList,
  UpdateExpenseInfo,
  ValidateUserRegistration
};
