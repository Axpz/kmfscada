"use client"

import React, { useState, useEffect, useCallback } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Thermometer, Gauge, Ruler, Factory, FlaskConical, LineChart, TrendingUp, Droplet, Cog, Cable
} from "lucide-react";
import {
  LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer
} from "recharts";

// Sparkline for Diameter Trend
const DiameterSparkline = ({ history }: { history: number[] }) => {
  if (!history || history.length < 2) return <div className="h-16 w-full flex items-center justify-center text-gray-500 text-xs">数据不足</div>;
  const maxVal = Math.max(...history);
  const minVal = Math.min(...history);
  const range = maxVal - minVal;
  return (
    <div className="relative w-full h-16 flex items-end overflow-hidden">
      {history.map((val, index) => {
        const height = range > 0 ? ((val - minVal) / range) * 100 : 0;
        const color = val > (history[index - 1] || val) ? 'bg-green-500' : val < (history[index - 1] || val) ? 'bg-red-500' : 'bg-blue-500';
        return (
          <div
            key={index}
            className={`flex-grow mx-px rounded-t-sm ${color}`}
            style={{ height: `${Math.max(5, height)}%` }}
          ></div>
        );
      })}
    </div>
  );
};

// Sparkline for Fluoride Concentration Trend
const FluorideSparkline = ({ history }: { history: number[] }) => {
  if (!history || history.length < 2) return <div className="h-16 w-full flex items-center justify-center text-gray-500 text-xs">数据不足</div>;
  const maxVal = Math.max(...history);
  const minVal = Math.min(...history);
  const range = maxVal - minVal;
  return (
    <div className="relative w-full h-16 flex items-end overflow-hidden">
      {history.map((val, index) => {
        const height = range > 0 ? ((val - minVal) / range) * 100 : 0;
        const color = val > (history[index - 1] || val) ? 'bg-blue-500' : val < (history[index - 1] || val) ? 'bg-orange-500' : 'bg-gray-500';
        return (
          <div
            key={index}
            className={`flex-grow mx-px rounded-t-sm ${color}`}
            style={{ height: `${Math.max(5, height)}%` }}
          ></div>
        );
      })}
    </div>
  );
};

// Custom Temperature Chart Component
const TemperatureChart = ({ data }: { data: any[] }) => (
  <ResponsiveContainer width="100%" height={180}>
    <RechartsLineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
      <XAxis dataKey="time" stroke="#cbd5e0" />
      <YAxis stroke="#cbd5e0" label={{ value: '温度 (°C)', angle: -90, position: 'insideLeft', fill: '#cbd5e0' }} />
      <RechartsTooltip contentStyle={{ backgroundColor: '#2d3748', border: '1px solid #4a5568', borderRadius: '0.5rem' }} labelStyle={{ color: '#e2e8f0' }} itemStyle={{ color: '#e2e8f0' }} />
      <Legend wrapperStyle={{ color: '#e2e8f0' }} />
      <Line type="monotone" dataKey="zone1" stroke="#8884d8" name="机身一区" activeDot={{ r: 8 }} />
      <Line type="monotone" dataKey="zone2" stroke="#82ca9d" name="机身二区" activeDot={{ r: 8 }} />
      <Line type="monotone" dataKey="zone3" stroke="#ffc658" name="机身三区" activeDot={{ r: 8 }} />
      <Line type="monotone" dataKey="zone4" stroke="#ff7300" name="机身四区" activeDot={{ r: 8 }} />
      <Line type="monotone" dataKey="flange" stroke="#a020f0" name="法兰温度" activeDot={{ r: 8 }} />
      <Line type="monotone" dataKey="moldZone1" stroke="#1e90ff" name="模具一区" activeDot={{ r: 8 }} />
      <Line type="monotone" dataKey="moldZone2" stroke="#32cd32" name="模具二区" activeDot={{ r: 8 }} />
    </RechartsLineChart>
  </ResponsiveContainer>
);

// Tooltip component
const Tooltip = ({ children, content }: { children: React.ReactNode, content: React.ReactNode }) => {
  const [show, setShow] = useState(false);
  return (
    <div className="relative flex items-center" onMouseEnter={() => setShow(true)} onMouseLeave={() => setShow(false)}>
      {children}
      {show && (
        <div className="absolute z-10 p-3 bg-gray-700 text-gray-100 text-xs rounded-lg shadow-lg -top-2 left-1/2 -translate-x-1/2 transform whitespace-nowrap border border-gray-600">
          {content}
        </div>
      )}
    </div>
  );
};

// Equipment Unit Component
interface EquipmentUnitProps {
  title: string;
  icon: React.ElementType;
  equipmentKey: string;
  bodyTemps?: any;
  flangeTemp?: number;
  moldTemps?: any;
  screwSpeed?: number;
  tractionSpd?: number;
  realtimeDiameter?: number;
  fluorideConc?: number;
}

const EquipmentUnit: React.FC<EquipmentUnitProps> = ({ title, icon: Icon, equipmentKey, bodyTemps = {}, flangeTemp = 0, moldTemps = {}, screwSpeed = 0, tractionSpd = 0, realtimeDiameter = 0, fluorideConc = 0 }) => {
  const getEquipmentStatus = useCallback((key: string) => {
    switch (key) {
      case 'production_body':
        if (bodyTemps.zone1 < 210 || bodyTemps.zone1 > 230) return 'warning';
        if (bodyTemps.zone1 < 200 || bodyTemps.zone1 > 240) return 'fault';
        return 'normal';
      case 'mold_body':
        if (moldTemps.zone1 < 190 || moldTemps.zone1 > 205) return 'warning';
        if (moldTemps.zone1 < 180 || moldTemps.zone1 > 210) return 'fault';
        return 'normal';
      case 'flange_area':
        if (flangeTemp < 200 || flangeTemp > 220) return 'warning';
        if (flangeTemp < 190 || flangeTemp > 230) return 'fault';
        return 'normal';
      case 'screw_motor_line1':
      case 'extruder':
        if (screwSpeed < 100 || screwSpeed > 150) return 'warning';
        if (screwSpeed < 80 || screwSpeed > 170) return 'fault';
        return 'normal';
      case 'traction_line1':
      case 'traction_machine':
        if (tractionSpd < 14 || tractionSpd > 16) return 'warning';
        if (tractionSpd < 13 || tractionSpd > 17) return 'fault';
        return 'normal';
      case 'online_detector':
        if (realtimeDiameter < 24.8 || realtimeDiameter > 25.2) return 'warning';
        if (realtimeDiameter < 24.5 || realtimeDiameter > 25.5) return 'fault';
        return 'normal';
      case 'cleaning_station':
        if (fluorideConc < 0.7 || fluorideConc > 0.9) return 'warning';
        if (fluorideConc < 0.6 || fluorideConc > 1.0) return 'fault';
        return 'normal';
      default:
        return 'normal';
    }
  }, [bodyTemps, flangeTemp, moldTemps, screwSpeed, tractionSpd, realtimeDiameter, fluorideConc]);

  const status = getEquipmentStatus(equipmentKey);
  let statusColorClass = 'bg-green-500';
  let statusBgClass = 'bg-gray-700';
  let statusBorderClass = 'border-blue-500';
  let statusText = '正常';
  let pulseClass = '';
  if (status === 'fault') {
    statusColorClass = 'bg-red-500';
    statusBgClass = 'bg-red-900/30';
    statusBorderClass = 'border-red-500';
    statusText = '故障';
    pulseClass = 'animate-pulse';
  } else if (status === 'warning') {
    statusColorClass = 'bg-yellow-500';
    statusBgClass = 'bg-yellow-900/30';
    statusBorderClass = 'border-yellow-500';
    statusText = '警告';
  }
  let displayData = null;
  switch (equipmentKey) {
    case 'production_body':
      displayData = (
        <div className="text-right text-xs text-gray-200 mt-1">
          <p>一区: {bodyTemps.zone1}°C</p>
          <p>二区: {bodyTemps.zone2}°C</p>
          <p>三区: {bodyTemps.zone3}°C</p>
          <p>四区: {bodyTemps.zone4}°C</p>
        </div>
      );
      break;
    case 'mold_body':
      displayData = (
        <div className="text-right text-xs text-gray-200 mt-1">
          <p>一区: {moldTemps.zone1}°C</p>
          <p>二区: {moldTemps.zone2}°C</p>
        </div>
      );
      break;
    case 'flange_area':
      displayData = <p className="text-right text-xs text-gray-200 mt-1">{flangeTemp}°C</p>;
      break;
    case 'screw_motor_line1':
    case 'extruder':
      displayData = <p className="text-right text-xs text-gray-200 mt-1">{screwSpeed} RPM</p>;
      break;
    case 'traction_line1':
    case 'traction_machine':
      displayData = <p className="text-right text-xs text-gray-200 mt-1">{tractionSpd} m/min</p>;
      break;
    case 'online_detector':
      displayData = <p className="text-right text-xs text-gray-200 mt-1">{realtimeDiameter} mm</p>;
      break;
    case 'cleaning_station':
      displayData = <p className="text-right text-xs text-gray-200 mt-1">{fluorideConc} ppm</p>;
      break;
    default:
      displayData = null;
  }
  const tooltipContent = (
    <div className="text-left">
      <p className="font-bold">{title}</p>
      <p>状态: <span className={`${status === 'fault' ? 'text-red-400' : status === 'warning' ? 'text-yellow-400' : 'text-green-400'}`}>{statusText}</span></p>
      {equipmentKey === 'production_body' && (
        <>
          <p>机身一区温度: {bodyTemps.zone1}°C</p>
          <p>机身二区温度: {bodyTemps.zone2}°C</p>
          <p>机身三区温度: {bodyTemps.zone3}°C</p>
          <p>机身四区温度: {bodyTemps.zone4}°C</p>
        </>
      )}
      {equipmentKey === 'mold_body' && (
        <>
          <p>模具一区温度: {moldTemps.zone1}°C</p>
          <p>模具二区温度: {moldTemps.zone2}°C</p>
        </>
      )}
      {equipmentKey === 'flange_area' && <p>法兰一个区温度: {flangeTemp}°C</p>}
      {equipmentKey === 'screw_motor_line1' && <p>螺杆电机转速: {screwSpeed} RPM</p>}
      {equipmentKey === 'traction_line1' && <p>牵引机速度: {tractionSpd} m/min</p>}
      {equipmentKey === 'extruder' && <p>螺杆电机转速: {screwSpeed} RPM</p>}
      {equipmentKey === 'online_detector' && <p>实时测量直径: {realtimeDiameter} mm</p>}
      {equipmentKey === 'traction_machine' && <p>牵引机速度: {tractionSpd} m/min</p>}
      {equipmentKey === 'cleaning_station' && <p>氟离子浓度: {fluorideConc} ppm</p>}
    </div>
  );
  return (
    <Tooltip content={tooltipContent}>
      <div className={`equipment-unit rounded-md p-3 flex items-start justify-between border ${statusBgClass} ${statusBorderClass} ${pulseClass} transition-all duration-300 hover:scale-105 flex-grow min-w-0`}>
        <div className="flex flex-col items-center mr-2">
          <div className={`status-indicator w-3 h-3 rounded-full ${statusColorClass} mb-2`}></div>
          {Icon && <Icon size={20} className="mb-1 text-blue-300" />}
          <span className="text-sm text-gray-200 text-center">{title}</span>
          {status !== 'normal' && <span className={`text-xs mt-1 ${status === 'fault' ? 'text-red-200' : 'text-yellow-200'}`}>{statusText}</span>}
        </div>
        <div className="flex-grow flex flex-col justify-end">
          {displayData}
        </div>
      </div>
    </Tooltip>
  );
};

// LineOverviewCard for consolidated line status
const LineOverviewCard = ({ lineName, pipelineNumber, batchNumber, currentBatchLength, oeePercentage }: {
  lineName: string;
  pipelineNumber: string;
  batchNumber: string;
  currentBatchLength: number;
  oeePercentage: number;
}) => (
  <Card className="bg-gray-800 border border-gray-700 flex flex-col items-center justify-center p-1 flex-grow min-w-0">
    <CardHeader className="p-0 pb-1 text-center">
      <CardTitle className="text-base font-bold text-blue-300 flex items-center justify-center whitespace-nowrap">
        <Factory className="mr-1" size={16} strokeWidth={1.5} />
        {lineName}
      </CardTitle>
    </CardHeader>
    <CardContent className="flex flex-col items-center justify-center p-0 pt-1 w-full">
      <div className="flex items-center justify-between text-gray-300 text-sm w-full mb-0.5">
        <span className="font-semibold whitespace-nowrap mr-1">流水线:</span>
        <span className="text-white font-bold whitespace-nowrap">{pipelineNumber}</span>
      </div>
      <div className="flex items-center justify-between text-gray-300 text-sm w-full mb-0.5">
        <span className="font-semibold whitespace-nowrap mr-1">批号:</span>
        <span className="text-white font-bold whitespace-nowrap">{batchNumber}</span>
      </div>
      <div className="flex items-center justify-between text-gray-300 text-sm w-full mb-1">
        <span className="font-semibold whitespace-nowrap mr-1">长度:</span>
        <span className="text-white font-bold whitespace-nowrap">{currentBatchLength} m</span>
      </div>
      <div className="relative w-16 h-16 mt-1">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          <circle className="text-gray-700" strokeWidth="5" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50" />
          <circle className="text-green-500 transition-all duration-1000 ease-in-out" strokeWidth="5" strokeDasharray={`${oeePercentage * 2.51}, 251`} strokeDashoffset="0" strokeLinecap="round" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50" transform="rotate(-90 50 50)" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-white text-lg font-bold">{oeePercentage}%</span>
        </div>
      </div>
      <p className="text-gray-400 text-sm mt-0.5 text-center">OEE</p>
    </CardContent>
  </Card>
);

// 主SCADA车间大屏组件
const ScadaWorkshopDashboard: React.FC = () => {
  // State variables for simulated data (detailed for Line 1, summary for others)
  const [line1DetailedData, setLine1DetailedData] = useState({
    bodyTemperatures: { zone1: 220, zone2: 225, zone3: 218, zone4: 222 },
    flangeTemperature: 210,
    moldTemperatures: { zone1: 195, zone2: 198 },
    screwMotorSpeed: 120,
    realtimeDiameter: 25.0,
    tractionSpeed: 15,
    currentBatchLength: 1500,
    fluorideConcentration: 0.8,
  });
  const [line1Summary, setLine1Summary] = useState({ pipelineNumber: 'PL-001', batchNumber: 'BATCH-20250708-001', currentBatchLength: 1500, oeePercentage: 85 });
  const [line2Summary, setLine2Summary] = useState({ pipelineNumber: 'PL-002', batchNumber: 'BATCH-20250708-002', currentBatchLength: 1200, oeePercentage: 88 });
  const [line3Summary, setLine3Summary] = useState({ pipelineNumber: 'PL-003', batchNumber: 'BATCH-20250708-003', currentBatchLength: 1800, oeePercentage: 92 });
  const [line4Summary, setLine4Summary] = useState({ pipelineNumber: 'PL-004', batchNumber: 'BATCH-20250708-004', currentBatchLength: 900, oeePercentage: 78 });
  const [diameterHistory, setDiameterHistory] = useState<number[]>([]);
  const [bodyTempHistory, setBodyTempHistory] = useState<any[]>([]);
  const [fluorideHistory, setFluorideHistory] = useState<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const timeString = now.toLocaleTimeString();
      const newBodyTemps = {
        zone1: parseFloat((line1DetailedData.bodyTemperatures.zone1 + (Math.random() * 2 - 1)).toFixed(1)),
        zone2: parseFloat((line1DetailedData.bodyTemperatures.zone2 + (Math.random() * 2 - 1)).toFixed(1)),
        zone3: parseFloat((line1DetailedData.bodyTemperatures.zone3 + (Math.random() * 2 - 1)).toFixed(1)),
        zone4: parseFloat((line1DetailedData.bodyTemperatures.zone4 + (Math.random() * 2 - 1)).toFixed(1)),
      };
      const newFlangeTemperature = parseFloat((line1DetailedData.flangeTemperature + (Math.random() * 1 - 0.5)).toFixed(1));
      const newMoldTemperatures = {
        zone1: parseFloat((line1DetailedData.moldTemperatures.zone1 + (Math.random() * 1 - 0.5)).toFixed(1)),
        zone2: parseFloat((line1DetailedData.moldTemperatures.zone2 + (Math.random() * 1 - 0.5)).toFixed(1)),
      };
      const newScrewMotorSpeed = parseFloat((line1DetailedData.screwMotorSpeed + (Math.random() * 5 - 2.5)).toFixed(0));
      const newRealtimeDiameter = parseFloat((25.0 + (Math.random() * 0.2 - 0.1)).toFixed(2));
      const newTractionSpeed = parseFloat((line1DetailedData.tractionSpeed + (Math.random() * 0.5 - 0.25)).toFixed(1));
      const newCurrentBatchLength = line1DetailedData.currentBatchLength + parseFloat((Math.random() * 10).toFixed(0));
      const newFluorideConcentration = parseFloat((0.8 + (Math.random() * 0.05 - 0.025)).toFixed(2));
      setLine1DetailedData({
        bodyTemperatures: newBodyTemps,
        flangeTemperature: newFlangeTemperature,
        moldTemperatures: newMoldTemperatures,
        screwMotorSpeed: newScrewMotorSpeed,
        realtimeDiameter: newRealtimeDiameter,
        tractionSpeed: newTractionSpeed,
        currentBatchLength: newCurrentBatchLength,
        fluorideConcentration: newFluorideConcentration,
      });
      setDiameterHistory(prevHistory => [...prevHistory.slice(-29), newRealtimeDiameter]);
      setFluorideHistory(prevHistory => [...prevHistory.slice(-29), newFluorideConcentration]);
      setBodyTempHistory(prevHistory => {
        const newChartDataPoint = {
          time: timeString,
          zone1: newBodyTemps.zone1,
          zone2: newBodyTemps.zone2,
          zone3: newBodyTemps.zone3,
          zone4: newBodyTemps.zone4,
          flange: newFlangeTemperature,
          moldZone1: newMoldTemperatures.zone1,
          moldZone2: newMoldTemperatures.zone2,
        };
        const updatedHistory = [...prevHistory, newChartDataPoint];
        return updatedHistory.slice(-20);
      });
      setLine1Summary(prev => ({ ...prev, currentBatchLength: prev.currentBatchLength + parseFloat((Math.random() * 10).toFixed(0)), oeePercentage: Math.max(70, Math.min(95, parseFloat((prev.oeePercentage + (Math.random() * 1 - 0.5)).toFixed(0)))) }));
      setLine2Summary(prev => ({ ...prev, currentBatchLength: prev.currentBatchLength + parseFloat((Math.random() * 10).toFixed(0)), oeePercentage: Math.max(70, Math.min(95, parseFloat((prev.oeePercentage + (Math.random() * 1 - 0.5)).toFixed(0)))) }));
      setLine3Summary(prev => ({ ...prev, currentBatchLength: prev.currentBatchLength + parseFloat((Math.random() * 10).toFixed(0)), oeePercentage: Math.max(70, Math.min(95, parseFloat((prev.oeePercentage + (Math.random() * 1 - 0.5)).toFixed(0)))) }));
      setLine4Summary(prev => ({ ...prev, currentBatchLength: prev.currentBatchLength + parseFloat((Math.random() * 10).toFixed(0)), oeePercentage: Math.max(70, Math.min(95, parseFloat((prev.oeePercentage + (Math.random() * 1 - 0.5)).toFixed(0)))) }));
    }, 1500);
    return () => clearInterval(interval);
  }, [line1DetailedData, line1Summary, line2Summary, line3Summary, line4Summary]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-gray-100 font-inter p-4 sm:p-6 lg:p-8">
      <header className="mb-8 text-center bg-gray-800/50 p-6 rounded-xl shadow-lg border border-gray-700 flex flex-col items-center justify-center">
        <h1 className="text-4xl font-extrabold text-blue-300 mb-2 tracking-wide">生产车间智能监控中心</h1>
        <p className="text-lg text-gray-400 mb-4">实时数据与车间概览</p>
        <div className="flex flex-row flex-nowrap justify-between w-full max-w-full overflow-x-auto pb-2">
          <LineOverviewCard lineName="一号线概览" {...line1Summary} />
          <LineOverviewCard lineName="二号线概览" {...line2Summary} />
          <LineOverviewCard lineName="三号线概览" {...line3Summary} />
          <LineOverviewCard lineName="四号线概览" {...line4Summary} />
        </div>
      </header>
      <div className="grid grid-cols-1 gap-6">
        <div className="space-y-6">
          <div className="workshop-diagram-container p-0 bg-gray-900 border border-gray-700 rounded-lg w-full">
            <div className="flex items-center justify-between mb-4 px-4 pt-4">
              <h2 className="text-xl font-bold text-blue-300 flex items-center">
                <Factory className="mr-2" size={24} strokeWidth={1.5} />
                生产车间布局
              </h2>
            </div>
            <div className="grid grid-cols-1 gap-6">
              {/* 一号线 */}
              <div className="line-section md:col-span-2 bg-gray-800 border border-gray-700 rounded-xl p-0">
                <div className="line-header text-blue-400 font-bold text-lg mb-2 px-4 pt-4">一号线</div>
                <div className="equipment-row flex flex-row flex-nowrap justify-between gap-2 overflow-x-auto pb-2 px-4">
                  <EquipmentUnit title="生产机身" icon={Cog} equipmentKey="production_body" bodyTemps={line1DetailedData.bodyTemperatures} />
                  <EquipmentUnit title="模具机身" icon={FlaskConical} equipmentKey="mold_body" moldTemps={line1DetailedData.moldTemperatures} />
                  <EquipmentUnit title="法兰" icon={Thermometer} equipmentKey="flange_area" flangeTemp={line1DetailedData.flangeTemperature} />
                  <EquipmentUnit title="螺杆电机" icon={Gauge} equipmentKey="screw_motor_line1" screwSpeed={line1DetailedData.screwMotorSpeed} />
                  <EquipmentUnit title="牵引机" icon={Cable} equipmentKey="traction_line1" tractionSpd={line1DetailedData.tractionSpeed} />
                </div>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Thermometer className="mr-2" size={20} strokeWidth={1.5} />关键温度趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <TemperatureChart data={bodyTempHistory} />
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <LineChart className="mr-2" size={20} strokeWidth={1.5} />实时直径趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <DiameterSparkline history={diameterHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4 mb-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Droplet className="mr-2" size={20} strokeWidth={1.5} />实时氟离子趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <FluorideSparkline history={fluorideHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
              </div>
              {/* 二号线 */}
              <div className="line-section md:col-span-2 bg-gray-800 border border-gray-700 rounded-xl p-0">
                <div className="line-header text-blue-400 font-bold text-lg mb-2 px-4 pt-4">二号线</div>
                <div className="equipment-row flex flex-row flex-nowrap justify-between gap-2 overflow-x-auto pb-2 px-4">
                  <EquipmentUnit title="生产机身" icon={Cog} equipmentKey="production_body_2" bodyTemps={line1DetailedData.bodyTemperatures} />
                  <EquipmentUnit title="模具机身" icon={FlaskConical} equipmentKey="mold_body_2" moldTemps={line1DetailedData.moldTemperatures} />
                  <EquipmentUnit title="法兰" icon={Thermometer} equipmentKey="flange_area_2" flangeTemp={line1DetailedData.flangeTemperature} />
                  <EquipmentUnit title="螺杆电机" icon={Gauge} equipmentKey="screw_motor_line2" screwSpeed={line1DetailedData.screwMotorSpeed} />
                  <EquipmentUnit title="牵引机" icon={Cable} equipmentKey="traction_line2" tractionSpd={line1DetailedData.tractionSpeed} />
                </div>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Thermometer className="mr-2" size={20} strokeWidth={1.5} />关键温度趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <TemperatureChart data={bodyTempHistory} />
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <LineChart className="mr-2" size={20} strokeWidth={1.5} />实时直径趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <DiameterSparkline history={diameterHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4 mb-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Droplet className="mr-2" size={20} strokeWidth={1.5} />实时氟离子趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <FluorideSparkline history={fluorideHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
              </div>
              {/* 三号线 */}
              <div className="line-section md:col-span-2 bg-gray-800 border border-gray-700 rounded-xl p-0">
                <div className="line-header text-blue-400 font-bold text-lg mb-2 px-4 pt-4">三号线</div>
                <div className="equipment-row flex flex-row flex-nowrap justify-between gap-2 overflow-x-auto pb-2 px-4">
                  <EquipmentUnit title="生产机身" icon={Cog} equipmentKey="production_body_3" bodyTemps={line1DetailedData.bodyTemperatures} />
                  <EquipmentUnit title="模具机身" icon={FlaskConical} equipmentKey="mold_body_3" moldTemps={line1DetailedData.moldTemperatures} />
                  <EquipmentUnit title="法兰" icon={Thermometer} equipmentKey="flange_area_3" flangeTemp={line1DetailedData.flangeTemperature} />
                  <EquipmentUnit title="螺杆电机" icon={Gauge} equipmentKey="screw_motor_line3" screwSpeed={line1DetailedData.screwMotorSpeed} />
                  <EquipmentUnit title="牵引机" icon={Cable} equipmentKey="traction_line3" tractionSpd={line1DetailedData.tractionSpeed} />
                </div>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Thermometer className="mr-2" size={20} strokeWidth={1.5} />关键温度趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <TemperatureChart data={bodyTempHistory} />
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <LineChart className="mr-2" size={20} strokeWidth={1.5} />实时直径趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <DiameterSparkline history={diameterHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4 mb-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Droplet className="mr-2" size={20} strokeWidth={1.5} />实时氟离子趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <FluorideSparkline history={fluorideHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
              </div>
              {/* 四号线 */}
              <div className="line-section md:col-span-2 bg-gray-800 border border-gray-700 rounded-xl p-0">
                <div className="line-header text-blue-400 font-bold text-lg mb-2 px-4 pt-4">四号线</div>
                <div className="equipment-row flex flex-row flex-nowrap justify-between gap-2 overflow-x-auto pb-2 px-4">
                  <EquipmentUnit title="生产机身" icon={Cog} equipmentKey="production_body_4" bodyTemps={line1DetailedData.bodyTemperatures} />
                  <EquipmentUnit title="模具机身" icon={FlaskConical} equipmentKey="mold_body_4" moldTemps={line1DetailedData.moldTemperatures} />
                  <EquipmentUnit title="法兰" icon={Thermometer} equipmentKey="flange_area_4" flangeTemp={line1DetailedData.flangeTemperature} />
                  <EquipmentUnit title="螺杆电机" icon={Gauge} equipmentKey="screw_motor_line4" screwSpeed={line1DetailedData.screwMotorSpeed} />
                  <EquipmentUnit title="牵引机" icon={Cable} equipmentKey="traction_line4" tractionSpd={line1DetailedData.tractionSpeed} />
                </div>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Thermometer className="mr-2" size={20} strokeWidth={1.5} />关键温度趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <TemperatureChart data={bodyTempHistory} />
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <LineChart className="mr-2" size={20} strokeWidth={1.5} />实时直径趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <DiameterSparkline history={diameterHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
                <Card className="bg-gray-700/50 border border-gray-600 mt-4 mx-4 mb-4">
                  <CardHeader className="px-4 pt-4 pb-2">
                    <CardTitle className="text-lg font-bold text-blue-200 flex items-center">
                      <Droplet className="mr-2" size={20} strokeWidth={1.5} />实时氟离子趋势
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <FluorideSparkline history={fluorideHistory} />
                    <p className="text-gray-400 text-sm mt-4 text-center">最近30次测量值</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </div>
      <footer className="mt-8 text-center text-gray-500 text-sm">
        <p>&copy; 2025 生产车间智能监控中心. All rights reserved.</p>
      </footer>
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
        @keyframes pulse-red {
          0% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(229, 62, 62, 0); }
          100% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }
        }
        .animate-pulse { animation: pulse-red 1.5s infinite; }
      `}</style>
    </div>
  );
};

export default ScadaWorkshopDashboard; 