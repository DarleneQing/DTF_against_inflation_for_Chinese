#########loading data
install.packages("openxlsx")
install.packages("plotly")
install.packages("orca")
install.packages("magrittr")
library(magrittr)
library(openxlsx)
library(zoo)
library(readxl)
library(ggplot2)
library(dplyr)
library(tidyr)
library(stargazer)
library(car)
library(plotly)
library(orca)
library(Hmisc)
library(knitr)

excel_file_path <- "/Users/yujuechen/Downloads/Digital tools for finance/data.xlsx"
data <- read_excel(excel_file_path)
# Convert quarters to a Date format
data$Time <- as.Date(paste0(data$Time, "-01"), format = "%Y-%m-%d")
data$core_inflation = data$core_inflation * 100
data$headline_inflation = data$headline_inflation * 100
data$government_bond_yield_sixm = data$government_bond_yield_sixm * 100
data$government_bond_yield_fivey = data$government_bond_yield_fivey * 100
data$government_bond_yield_teny = data$government_bond_yield_teny * 100
label(data$House_price) = "(CNY/m^2)"
label(data$Gold_price) = "(CNY/gram)"
label(data$Fixed_deposit_rate) = "percentage%"
label(data$Shanghai_stock_index) = "point"
label(data$core_inflation) = "percentage%"
label(data$headline_inflation) = "percentage%"
label(data$government_bond_yield_sixm) = "government_bond_yield(6-month), percentage%"
label(data$government_bond_yield_fivey) = "government_bond_yield(5-year), percentage%"
label(data$government_bond_yield_teny) = "government_bond_yield(10-year), percentage%"



#####This part analysis the original data with mean, variance etc.

c1 <- c("House_price", "Gold_price", "Fixed_deposit_rate", "Shanghai_stock_index", 
        "government_bond_yield_sixm", "government_bond_yield_fivey", "government_bond_yield_teny")
summary_data <- data.frame(
  Mean = sapply(data[, c1], mean),
  SD = sapply(data[, c1], sd),
  Min = sapply(data[, c1], min),
  Max = sapply(data[, c1], max)
)
summary_data
my_table <- kable(summary_data, format = "latex", caption = "Assets Data", booktabs = TRUE)
print(my_table)

#First, figure out the relationships between assets and inflation separately
# Calculate the percentage change for each time point - quarter
# 1.house prise, 2.gold price, 3.shanghai stock composite index, 
colnames(data)
data <- data %>%
  fill(core_inflation, .direction = "down") %>%
  mutate(House_Change = (House_price - lag(House_price)) / lag(House_price) * 100,
         Gold_Change = (Gold_price - lag(Gold_price)) / lag(Gold_price) * 100,
         Shanghai_stock_Change = (Shanghai_stock_index - lag(Shanghai_stock_index)) / lag(Shanghai_stock_index) * 100)
#Replace NA with second row as default value
data$House_Change[1] <- data$House_Change[2]
data$Gold_Change[1] <- data$Gold_Change[2]
data$Shanghai_stock_Change[1] <- data$Shanghai_stock_Change[2]

# Calculate the return rate - Asset/Inflation
data <- data %>%
  mutate(House_proportion = House_Change / core_inflation,
         Gold_proportion = Gold_Change / core_inflation,
         Fixed_deposit_proportion = Fixed_deposit_rate / core_inflation,
         Shanghai_stock_proportion = Shanghai_stock_Change / core_inflation,
         Gover_sixm_proportion = government_bond_yield_sixm / core_inflation,
         Gover_fivey_proportion = government_bond_yield_fivey / core_inflation,
         Gover_teny_proportion = government_bond_yield_teny / core_inflation)

#Draw the plot change percentage
#plot(data$Time, data$House_proportion, type = "l", col = "blue", xlab = "Time", ylab = "Asset/Inflation", main = "Multiple Lines for Each asset vs. inflation Over Time", ylim = c(-14,14))
#lines(data$Time, data$Gold_proportion, col = "red")
#lines(data$Time, data$Fixed_deposit_proportion, col = "green")
#lines(data$Time, data$Shanghai_stock_proportion, col = "yellow")
#lines(data$Time, data$Gover_sixm_proportion, col = "orange")
#lines(data$Time, data$Gover_fivey_proportion, col = "purple")
#lines(data$Time, data$Gover_teny_proportion, col = "cyan")
#legend("bottomleft", legend = c("House", "Gold", "Fixed deposit rate", "Shanghai stock index", 
#                                "government six months", "government five years", 
#                                "government ten years"), 
#       col = c("blue", "red", "green", "yellow", "orange", "purple", "cyan"), lty = 1, cex = 0.8)

# Interactive plot - (Time - (asset / inflatinon))
plot_ly(data, x = ~Time, y = ~House_proportion, type = "scatter", mode = "lines", line = list(color = 'blue'), name = "House") %>%
  add_trace(x = ~Time, y = ~Gold_proportion, type = "scatter", mode = "lines", line = list(color = 'red'), name = "Gold") %>%
  add_trace(x = ~Time, y = ~Fixed_deposit_proportion, type = "scatter", mode = "lines", line = list(color = 'green'), name = "Fixed Deposit") %>%
  add_trace(x = ~Time, y = ~Shanghai_stock_proportion, type = "scatter", mode = "lines", line = list(color = 'yellow'), name = "Shanghai Stock") %>%
  add_trace(x = ~Time, y = ~Gover_sixm_proportion, type = "scatter", mode = "lines", line = list(color = 'orange'), name = "Government Six Months") %>%
  add_trace(x = ~Time, y = ~Gover_fivey_proportion, type = "scatter", mode = "lines", line = list(color = 'purple'), name = "Government Five Years") %>%
  add_trace(x = ~Time, y = ~Gover_teny_proportion, type = "scatter", mode = "lines", line = list(color = 'cyan'), name = "Government Ten Years") %>%
  layout(title = "Multiple Lines for Each Asset vs. Inflation Over Time",
         xaxis = list(title = "Time"),
         yaxis = list(title = "return rate - Asset/Inflation"),
         legend = list(x = 0, y = -0.4),  # Adjust the legend position as needed
         updatemenus = list(
           list(type = "buttons",
                showactive = FALSE,
                buttons = list(
                  list(label = "Zoom In",
                       method = "relayout",
                       args = list("xaxis.range", list(0, 2))),  # Adjust the range as needed
                  list(label = "Zoom Out",
                       method = "relayout",
                       args = list("xaxis.range", list(0, 10)))  # Adjust the range as needed
                )
           )
         )
  )

#Sceond
colnames(data)
# Run regression house_property_price on log(core_inflation) and the other assets
lm_house_on_others <- lm(House_Change ~ log1p(core_inflation) + Gold_Change + Fixed_deposit_rate +
                           Shanghai_stock_Change + government_bond_yield_sixm + government_bond_yield_fivey +
                           government_bond_yield_teny, data = data)
summary(lm_house_on_others)

lm_gold_on_others <- lm(Gold_Change ~ log1p(core_inflation) + House_Change + Fixed_deposit_rate +
                          Shanghai_stock_Change + government_bond_yield_sixm + government_bond_yield_fivey +
                          government_bond_yield_teny, data = data)
summary(lm_gold_on_others)

lm_fixed_on_others <- lm(Fixed_deposit_rate ~ log1p(core_inflation) + House_Change + Gold_Change +
                           Shanghai_stock_Change + government_bond_yield_sixm + government_bond_yield_fivey +
                           government_bond_yield_teny, data = data)

lm_stock_on_others <- lm(Shanghai_stock_Change ~ log1p(core_inflation) + House_Change + Gold_Change +
                           Fixed_deposit_rate + government_bond_yield_sixm + government_bond_yield_fivey +
                           government_bond_yield_teny, data = data)

lm_sixm_on_others <- lm(government_bond_yield_sixm ~ log1p(core_inflation) + House_Change + Gold_Change +
                          Fixed_deposit_rate + Shanghai_stock_Change + government_bond_yield_fivey +
                          government_bond_yield_teny, data = data)

lm_fivey_on_others <- lm(government_bond_yield_fivey ~ log1p(core_inflation) + House_Change + Gold_Change +
                           Fixed_deposit_rate + Shanghai_stock_Change + government_bond_yield_sixm +
                           government_bond_yield_teny, data = data)

lm_teny_on_others <- lm(government_bond_yield_teny ~ log1p(core_inflation) + House_Change + Gold_Change +
                          Fixed_deposit_rate + Shanghai_stock_Change + government_bond_yield_sixm +
                          government_bond_yield_fivey, data = data)


models_all <- list(lm_house_on_others, lm_gold_on_others, lm_fixed_on_others, lm_stock_on_others)
model_names_all <- c("house", "gold", "fixed", "stock")
stargazer(models_all, title = "Regression Models", align = TRUE, column.labels = model_names_all, type = "text")



models_2 <- list(lm_sixm_on_others, lm_fivey_on_others, lm_teny_on_others)
model_names_2 <- c("sixm", "fivey", "teny")
stargazer(models_2, title = "Regression Models", align = TRUE, column.labels = model_names_2,  type = "latex")

#check correlation between different assets
col_corr <- c("House_Change", "Gold_Change", "Fixed_deposit_rate", "Shanghai_stock_Change",
              "government_bond_yield_sixm", "government_bond_yield_fivey", "government_bond_yield_teny")
data_corr <- data[,col_corr]
correlation_matrix <- cor(data_corr)
correlation_matrix


#according correlation and p values adjust the model if 0.00 to 0.19: Very weak correlation
lm_house_on_others_new <- lm(House_Change ~ log1p(core_inflation) + government_bond_yield_sixm + 
                             government_bond_yield_fivey + government_bond_yield_teny, data = data)

lm_gold_on_others_new <- lm(Gold_Change ~ log1p(core_inflation) + Shanghai_stock_Change + 
                            government_bond_yield_sixm + government_bond_yield_fivey +
                            government_bond_yield_teny, data = data)

lm_fixed_on_others_new <- lm(Fixed_deposit_rate ~ log1p(core_inflation) + House_Change + 
                               government_bond_yield_sixm + government_bond_yield_fivey +
                               government_bond_yield_teny, data = data)

lm_stock_on_others_new <- lm(Shanghai_stock_Change ~ log1p(core_inflation) + Gold_Change, 
                             data = data)

lm_sixm_on_others_new <- lm(government_bond_yield_sixm ~ log1p(core_inflation) + House_Change + Gold_Change +
                              Fixed_deposit_rate + government_bond_yield_fivey +
                              government_bond_yield_teny, data = data)

lm_fivey_on_others_new <- lm(government_bond_yield_fivey ~ log1p(core_inflation) + House_Change + Gold_Change +
                               Fixed_deposit_rate + government_bond_yield_sixm +
                               government_bond_yield_teny, data = data)

lm_teny_on_others_new <- lm(government_bond_yield_teny ~ log1p(core_inflation) + House_Change + Gold_Change +
                              Fixed_deposit_rate + government_bond_yield_sixm +
                              government_bond_yield_fivey, data = data)


models_all_new <- list(lm_house_on_others_new, lm_gold_on_others_new, lm_fixed_on_others_new, lm_stock_on_others_new)
model_names_all <- c("house", "gold", "fixed", "stock")
stargazer(models_all_new, title = "Regression Models", align = TRUE, column.labels = model_names_all, type = "latex")

models_2_new <- list(lm_sixm_on_others_new, lm_fivey_on_others_new, lm_teny_on_others_new)
model_names_2 <- c("sixm", "fivey", "teny")
stargazer(models_2_new, title = "Regression Models", align = TRUE, column.labels = model_names_2, type = "latex")

# check the assumptions for lm_house_on_others_new
# Check linearity
plot(lm_house_on_others_new)
# Check independence of residuals
plot(residuals(lm_house_on_others_new) ~ predict(lm_house_on_others_new))
# Check homoscedasticity
plot(predict(lm_house_on_others_new), residuals(lm_house_on_others_new))
# Check normality of residuals
hist(residuals(lm_house_on_others_new))
qqnorm(residuals(lm_house_on_others_new))
qqline(residuals(lm_house_on_others_new))
# Check multicollinearity (for multiple predictors)
#IF = 1: No correlation. The variance of the coefficient is not inflated.
#VIF between 1 and 5: Moderate correlation. The variance of the coefficient is moderately inflated.
#VIF > 5: High correlation. The variance of the coefficient is highly inflated.
vif(lm_house_on_others_new)

#lm_gold_on_others_new
# Check linearity
plot(lm_gold_on_others_new)
# Check independence of residuals
plot(residuals(lm_gold_on_others_new) ~ predict(lm_gold_on_others_new))
# Check homoscedasticity
plot(predict(lm_gold_on_others_new), residuals(lm_gold_on_others_new))
# Check normality of residuals
hist(residuals(lm_gold_on_others_new))
qqnorm(residuals(lm_gold_on_others_new))
qqline(residuals(lm_gold_on_others_new))
# Check multicollinearity (for multiple predictors)
vif(lm_gold_on_others_new)


#lm_fixed_on_others_new
# Check linearity
plot(lm_fixed_on_others_new)
# Check independence of residuals
plot(residuals(lm_fixed_on_others_new) ~ predict(lm_fixed_on_others_new))
# Check homoscedasticity
plot(predict(lm_fixed_on_others_new), residuals(lm_fixed_on_others_new))
# Check normality of residuals
hist(residuals(lm_fixed_on_others_new))
qqnorm(residuals(lm_fixed_on_others_new))
qqline(residuals(lm_fixed_on_others_new))
# Check multicollinearity (for multiple predictors)
vif(lm_fixed_on_others_new)

#lm_stock_on_others_new
# Check linearity
plot(lm_stock_on_others_new)
# Check independence of residuals
plot(residuals(lm_stock_on_others_new) ~ predict(lm_stock_on_others_new))
# Check homoscedasticity
plot(predict(lm_stock_on_others_new), residuals(lm_stock_on_others_new))
# Check normality of residuals
hist(residuals(lm_stock_on_others_new))
qqnorm(residuals(lm_stock_on_others_new))
qqline(residuals(lm_stock_on_others_new))
# Check multicollinearity (for multiple predictors)
vif(lm_stock_on_others_new)

#lm_sixm_on_others_new
# Check linearity
plot(lm_sixm_on_others_new)
# Check independence of residuals
plot(residuals(lm_sixm_on_others_new) ~ predict(lm_sixm_on_others_new))
# Check homoscedasticity
plot(predict(lm_sixm_on_others_new), residuals(lm_sixm_on_others_new))
# Check normality of residuals
hist(residuals(lm_sixm_on_others_new))
qqnorm(residuals(lm_sixm_on_others_new))
qqline(residuals(lm_sixm_on_others_new))
# Check multicollinearity (for multiple predictors)
vif(lm_sixm_on_others_new)

#lm_fivey_on_others_new
# Check linearity
plot(lm_fivey_on_others_new)
# Check independence of residuals
plot(residuals(lm_fivey_on_others_new) ~ predict(lm_fivey_on_others_new))
# Check homoscedasticity
plot(predict(lm_fivey_on_others_new), residuals(lm_fivey_on_others_new))
# Check normality of residuals
hist(residuals(lm_fivey_on_others_new))
qqnorm(residuals(lm_fivey_on_others_new))
qqline(residuals(lm_fivey_on_others_new))
# Check multicollinearity (for multiple predictors)
vif(lm_fivey_on_others_new)

#lm_teny_on_others_new
# Check linearity
plot(lm_teny_on_others_new)
# Check independence of residuals
plot(residuals(lm_teny_on_others_new) ~ predict(lm_teny_on_others_new))
# Check homoscedasticity
plot(predict(lm_teny_on_others_new), residuals(lm_teny_on_others_new))
# Check normality of residuals
hist(residuals(lm_teny_on_others_new))
qqnorm(residuals(lm_teny_on_others_new))
qqline(residuals(lm_teny_on_others_new))
# Check multicollinearity (for multiple predictors)
vif(lm_teny_on_others_new)


#install.packages(c('IRkernel', 'repr', 'IRdisplay', 'pbdZMQ', 'devtools'))
#devtools::install_github('IRkernel/IRkernel')
#IRkernel::installspec(user = FALSE)



