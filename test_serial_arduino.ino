void DisplayData(){
    String system_status;
    if (lastState == 1) {
        system_status = "Maintenance";
    } else if (lastState == 2) {
        system_status = "High Wind";
    } else if (lastState == 3) {
        system_status = "Low Battery";
    } else if (lastState == 4) {
        system_status = "Cold Weather";
    } else if (lastState == 5) {
        system_status = "Overnight";
    } else {
        system_status = "Normal";
    }

    String AzimMode;
    if (digitalRead(M1SelectMode) == HIGH) {
        AzimMode = "Automatic";
    } else {
        AzimMode = "Manual";
    }

    String AzimStatus;
    if (M1Running == 1) {
        if (digitalRead(M1Direction) == LOW) {
            AzimStatus = "CCW";
        } else {
            AzimStatus = "CW";
        }
    } else {
        AzimStatus = "OFF";
    }

    String ElevMode;
    if (digitalRead(M2SelectMode) == HIGH) {
        ElevMode = "Automatic";
    } else {
        ElevMode = "Manual";
    }
    String ElevStatus;
    if (M2Running == 1) {
        if (digitalRead(M2Direction) == LOW) {
            ElevStatus = "CCW";
        } else {
            ElevStatus = "CW";
        }
    } else {
        ElevStatus = "OFF";
    }
    String date_time;
    Clock.printDateTo_YMD(date_time);
    Clock.printTimeTo_HMS(date_time);
    Serial.println("LOG");
    char buffer[256];
    sprintf( buffer,
        "{'Date_Time': %s, 'System_Status': %s, 'Solar_Panel_Voltage': %f, "
        "'Solar_Panel_Current': %f, 'Solar_Panel_Power': %f, "
        "'Battery_One_Voltage': %f, 'Battery_Two_Voltage': %f, "
        "'Battery_Total_Voltage': %f, 'Battery_Total_Current': %f, "
        "'Load_Voltage': %f, 'Load_Current': %f, 'Load_Power': %f, "
        "'Inverter_Voltage': %f, 'Inverter_Current': %f, 'Inverter_Power': %f, "
        "'Motor_One_Voltage': %f, 'Motor_One_Current': %f, 'Motor_One_Power': "
        "%f, 'Motor_Two_Voltage': %f, 'Motor_Two_Current': %f, "
        "'Motor_Two_Power': %f, 'Five_Volt_Voltage': %f, 'Five_Volt_Current': "
        "%f, 'Five_Volt_Power': %f, 'Windspeed': %f, 'Outdoor_Temp': %f, "
        "'Outdoor_Humidity': %f, 'Azimuth_Reading': %f, 'Azimuth_Command': %f, "
        "'Azimuth_Motor_Mode': %f, 'Azimuth_Motor_Status': %f, "
        "'Elevation_Reading': %f, 'Elevation_Command': %f, "
        "'Elevation_Motor_Mode': %f, 'Elevation_Motor_Status': %f}",
        date_time, system_status, PanelVoltageHigh - PanelVoltageLow,
        PanelCurrent, (PanelVoltageHigh - PanelVoltageLow) * PanelCurrent,
        BatteryOneVoltage, BatteryTotalVoltage - BatteryOneVoltage,
        BatteryTotalVoltage, BatteryCurrent,
        BatteryTotalVoltage * BatteryCurrent, LoadVoltage, LoadCurrent,
        LoadVoltage * LoadCurrent, LoadVoltage, InverterCurrent,
        LoadVoltage * InverterCurrent, LoadVoltage, MotorOneCurrent,
        LoadVoltage * MotorOneCurrent, LoadVoltage, MotorTwoCurrent,
        LoadVoltage * MotorTwoCurrent, FiveVoltVoltage, FiveVoltCurrent,
        FiveVoltVoltage * FiveVoltCurrent, WindSpeed, OutdoorTemp,
        OutdoorHumidity, AzimuthReading, AzimuthCommand, AzimMode, AzimStatus,
        ElevationReading, ElevationCurrent, ElevMode, ElevStatus);
}