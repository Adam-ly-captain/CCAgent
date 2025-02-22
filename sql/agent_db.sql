/*
 Navicat Premium Dump SQL

 Source Server         : aliyun
 Source Server Type    : MySQL
 Source Server Version : 80041 (8.0.41-0ubuntu0.22.04.1)
 Source Host           : 8.134.39.162:3306
 Source Schema         : agent

 Target Server Type    : MySQL
 Target Server Version : 80041 (8.0.41-0ubuntu0.22.04.1)
 File Encoding         : 65001

 Date: 22/02/2025 16:34:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app_operation_log
-- ----------------------------
DROP TABLE IF EXISTS `app_operation_log`;
CREATE TABLE `app_operation_log`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `create_time` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 130 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for ui_control
-- ----------------------------
DROP TABLE IF EXISTS `ui_control`;
CREATE TABLE `ui_control`  (
  `id` int NOT NULL,
  `app_log_id` int NOT NULL,
  `left` int NULL DEFAULT NULL,
  `top` int NULL DEFAULT NULL,
  `right` int NULL DEFAULT NULL,
  `bottom` int NULL DEFAULT NULL,
  `label` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`id`, `app_log_id`) USING BTREE,
  INDEX `appid`(`app_log_id` ASC) USING BTREE,
  CONSTRAINT `appid` FOREIGN KEY (`app_log_id`) REFERENCES `app_operation_log` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
