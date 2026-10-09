import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text, View, ActivityIndicator } from "react-native";

import { useAuth } from "../context/AuthContext";
import { LoginScreen } from "../screens/auth/LoginScreen";
import { RegisterScreen } from "../screens/auth/RegisterScreen";
import { ForgotPasswordScreen } from "../screens/auth/ForgotPasswordScreen";
import { SymptomAssessmentScreen } from "../screens/patient/SymptomAssessmentScreen";
import { HistoryScreen } from "../screens/patient/HistoryScreen";
import { ClinicalAssistantScreen } from "../screens/doctor/ClinicalAssistantScreen";
import { AdminOverviewScreen } from "../screens/admin/AdminOverviewScreen";
import { ProfileScreen } from "../screens/profile/ProfileScreen";

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const TabIcon = ({ label, focused }: { label: string; focused: boolean }) => (
  <View style={{ alignItems: "center", justifyContent: "center" }}>
    <Text style={{ fontSize: 16, opacity: focused ? 1 : 0.6 }}>{label}</Text>
  </View>
);

const MainTabs = () => {
  const { user } = useAuth();
  const role = user?.role || "PATIENT";

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: "#0d9488",
        tabBarInactiveTintColor: "#64748b",
      }}
    >
      {role === "PATIENT" && (
        <>
          <Tab.Screen
            name="Assessment"
            component={SymptomAssessmentScreen}
            options={{ tabBarIcon: ({ focused }) => <TabIcon label="🩺" focused={focused} /> }}
          />
          <Tab.Screen
            name="History"
            component={HistoryScreen}
            options={{ tabBarIcon: ({ focused }) => <TabIcon label="📋" focused={focused} /> }}
          />
        </>
      )}

      {(role === "DOCTOR" || role === "PHARMACIST") && (
        <Tab.Screen
          name="Clinical Assistant"
          component={ClinicalAssistantScreen}
          options={{ tabBarIcon: ({ focused }) => <TabIcon label="👨‍⚕️" focused={focused} /> }}
        />
      )}

      {role === "ADMIN" && (
        <>
          <Tab.Screen
            name="Admin"
            component={AdminOverviewScreen}
            options={{ tabBarIcon: ({ focused }) => <TabIcon label="⚙️" focused={focused} /> }}
          />
          <Tab.Screen
            name="Clinical Assistant"
            component={ClinicalAssistantScreen}
            options={{ tabBarIcon: ({ focused }) => <TabIcon label="👨‍⚕️" focused={focused} /> }}
          />
        </>
      )}

      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ tabBarIcon: ({ focused }) => <TabIcon label="👤" focused={focused} /> }}
      />
    </Tab.Navigator>
  );
};

export const AppNavigator = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#0d9488" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {user ? (
          <Stack.Screen name="Main" component={MainTabs} />
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
            <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};
