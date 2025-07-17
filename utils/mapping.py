# Copyright 2025 Mahesh Pimpale
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# These are the clusters generated from single cluster file with multiple cluster ids hence it's commands will not be having any callbacks
command_callback_skip_list = [
    "joint_fabric_datastore",
    "joint_fabric_pki",
    "energy_price",
    "humidistat",
    "network_identity_management",
    "valid_proxies",
    "water_tank_level_monitoring",
    "carbon_dioxide_concentration_measurement",
    "carbon_monoxide_concentration_measurement",
    "nitrogen_dioxide_concentration_measurement",
    "ozone_concentration_measurement",
    "pm2_5_concentration_measurement",
    "pm1_concentration_measurement",
    "pm10_concentration_measurement",
    "formaldehyde_concentration_measurement",
    "total_volatile_organic_compounds_concentration_measurement",
    "radon_concentration_measurement",
    "closure_1st_dimension",
    "closure_2nd_dimension",
    "closure_3rd_dimension",
    "closure_4th_dimension",
    "closure_5th_dimension",
    "energy_tariff",
    "webrtc_transport_provider",
    "webrtc_transport_requestor",
    "soil_measurement",
    "camera_av_stream_management",
    "bridged_device_basic_information",
    "alarm_base",
    "mode_base",
]

# Cluster names are mapped to work with the existing code
cluster_name_mapping = {
    "Node Operational Credentials": "Operational Credentials",
    "Demand Response and Load Control": "Demand Response Load Control",
    "WakeOnLAN": "Wake on LAN",
    "OnOff": "On/Off",
    "ota_provider": "ota_software_update_provider",
    "ota_requestor": "ota_software_update_requestor",
}

# C++ reserved words
cpp_reserved_words = [
    "auto",
    "switch",
    "case",
    "default",
    "enum",
    "struct",
    "union",
    "typedef",
    "using",
    "static",
    "const",
    "volatile",
    "inline",
    "extern",
    "register",
    "restrict",
    "typeof",
    "void",
    "char",
    "short",
    "int",
    "long",
    "float",
    "double",
    "signed",
    "unsigned",
    "bool",
    "true",
    "false",
    "nullptr",
    "new",
    "delete",
    "try",
    "catch",
    "throw",
    "public",
    "private",
    "protected",
    "virtual",
    "override",
    "final",
    "explicit",
    "namespace",
    "using",
    "static_cast",
    "dynamic_cast",
    "reinterpret_cast",
    "const_cast",
    "static_assert",
    "thread_local",
    "constexpr",
    "constinit",
    "co_await",
    "co_return",
    "co_yield",
    "co_await",
    "co_return",
    "co_yield",
]

# These commands are declared in app-common/zap-generated/callback.h but they don't have implementation in connectedhomeip
callback_skip_list = [
    "MoveToClosestFrequency",
]
