-- khan.lua: links to the matching Khan Academy "Statistics essentials" lessons.
--
-- {{< khan 1.4 1.5 >}}      block: "Khan Academy: Unit 1, Lesson 4 ... , Lesson 5 ..."
-- {{< khanlink 1.4 >}}       inline link "Unit 1, lesson 4", for tables
-- {{< khanlink 1.4 "4" >}}   same link with your own text
--
-- Keys are Khan's own numbering: <unit>.<lesson>.  Paths come from the course
-- page (teacher library links with "/teacher/library/en" removed).

local BASE = "https://www.khanacademy.org/"

local LESSONS = {
  ["1.1"] = { title = "Frequency tables and dot plots", path = "math/math-essentials/probability/xa88397b6:display-quantitative/xa88397b6:frequency-tables-dot-plots" },
  ["1.2"] = { title = "Histograms", path = "math/math-essentials/probability/xa88397b6:display-quantitative/xa88397b6:histograms" },
  ["1.3"] = { title = "Mean and median in data displays", path = "math/math-essentials/probability/xa88397b6:display-quantitative/xa88397b6:mean-median-data-displays" },
  ["1.4"] = { title = "Interquartile range", path = "math/math-essentials/probability/xa88397b6:display-quantitative/xa88397b6:interquartile-range" },
  ["1.5"] = { title = "Box and whisker plots", path = "math/math-essentials/probability/xa88397b6:display-quantitative/box--whisker-plots-a1" },
  ["2.1"] = { title = "Standard deviation", path = "math/math-essentials/probability/xa88397b6:analyze-quantitative/xa88397b6:standard-deviation" },
  ["2.2"] = { title = "Comparing distributions", path = "math/math-essentials/probability/xa88397b6:analyze-quantitative/xa88397b6:untitled-193" },
  ["2.3"] = { title = "Percentiles and z-scores", path = "math/math-essentials/probability/xa88397b6:analyze-quantitative/xa88397b6:percentiles-z-scores" },
  ["2.4"] = { title = "Normal distributions and the empirical rule", path = "math/math-essentials/probability/xa88397b6:analyze-quantitative/normal-distributions-a2ii" },
  ["2.5"] = { title = "Normal distribution calculations", path = "math/math-essentials/probability/xa88397b6:analyze-quantitative/xa88397b6:normal-distribution-calculations" },
  ["3.1"] = { title = "Two-way tables introduction", path = "math/math-essentials/probability/xa88397b6:two-way-tables/two-way-frequency-tables" },
  ["3.2"] = { title = "Distributions in two-way tables", path = "math/math-essentials/probability/xa88397b6:two-way-tables/two-way-relative-frequency-tables" },
  ["4.1"] = { title = "Fitting trend lines to scatterplots", path = "math/math-essentials/probability/xa88397b6:scatterplots/creating-interpreting-scatterplots" },
  ["4.2"] = { title = "Analyzing trend lines in scatterplots", path = "math/math-essentials/probability/xa88397b6:scatterplots/estimating-trend-lines" },
  ["4.3"] = { title = "Residuals", path = "math/math-essentials/probability/xa88397b6:scatterplots/xa88397b6:residuals" },
  ["5.1"] = { title = "Introduction to planning a study", path = "math/math-essentials/probability/xa88397b6:study-design/samples-surveys" },
  ["5.2"] = { title = "Potential problems with sampling", path = "math/math-essentials/probability/xa88397b6:study-design/xa88397b6:potential-problems-sampling" },
  ["5.3"] = { title = "Sampling methods", path = "math/math-essentials/probability/xa88397b6:study-design/xa88397b6:sampling-methods" },
  ["5.4"] = { title = "Introduction to experimental design", path = "math/math-essentials/probability/xa88397b6:study-design/observational-studies-experiments" },
  ["5.5"] = { title = "Inference and experiments", path = "math/math-essentials/probability/xa88397b6:study-design/xa88397b6:inference-experiments" },
  ["6.1"] = { title = "Venn diagrams and the addition rule", path = "math/math-essentials/probability/xa88397b6:probability/addition-rule-for-probability" },
  ["6.2"] = { title = "Multiplication rule for probabilities", path = "math/math-essentials/probability/xa88397b6:probability/xa88397b6:multiplication-rule" },
  ["6.3"] = { title = "Conditional probability", path = "math/math-essentials/probability/xa88397b6:probability/conditional-probability-geo" },
  ["6.4"] = { title = "Probability from simulations", path = "math/math-essentials/probability/xa88397b6:probability/xa88397b6:probability-from-simulations" },
  ["6.5"] = { title = "Permutations", path = "math/math-essentials/probability/xa88397b6:probability/counting-permutations" },
  ["6.6"] = { title = "Combinations", path = "math/math-essentials/probability/xa88397b6:probability/counting-combinations" },
  ["6.7"] = { title = "Probability using combinatorics", path = "math/math-essentials/probability/xa88397b6:probability/probability-counting-permutations-combinations" },
  ["7.1"] = { title = "Probability distributions introduction", path = "math/math-essentials/probability/xa88397b6:probability-distributions-expected-value/xa88397b6:probability-distributions-introduction" },
  ["7.2"] = { title = "Theoretical & empirical probability distributions", path = "math/math-essentials/probability/xa88397b6:probability-distributions-expected-value/xa88397b6:theoretical-empirical-probability-distributions" },
  ["7.3"] = { title = "Decisions with probability", path = "math/math-essentials/probability/xa88397b6:probability-distributions-expected-value/xa88397b6:decisions-probability" },
  ["7.4"] = { title = "Expected value", path = "math/math-essentials/probability/xa88397b6:probability-distributions-expected-value/expected-value-geo" },
}

local function lookup(key)
  local l = LESSONS[key]
  if not l then
    return nil
  end
  local unit, lesson = key:match("^(%d+)%.(%d+)$")
  return l, unit, lesson
end

local function link(key, text)
  local l = lookup(key)
  if not l then
    return pandoc.Strong({ pandoc.Str("[unknown Khan lesson " .. key .. "]") })
  end
  return pandoc.Link({ pandoc.Str(text) }, BASE .. l.path, "", { target = "_blank" })
end

return {
  ["khan"] = function(args)
    local inlines = { pandoc.Strong({ pandoc.Str("Khan Academy:") }), pandoc.Space() }
    for i, a in ipairs(args) do
      local key = pandoc.utils.stringify(a)
      local l, unit, lesson = lookup(key)
      if i > 1 then
        table.insert(inlines, pandoc.Str(";"))
        table.insert(inlines, pandoc.Space())
      end
      if l then
        table.insert(inlines, link(key, "Unit " .. unit .. ", Lesson " .. lesson .. ": " .. l.title))
      else
        table.insert(inlines, link(key, key))
      end
    end
    return pandoc.Div({ pandoc.Para(inlines) }, pandoc.Attr("", { "khan-link" }))
  end,

  ["khanlink"] = function(args)
    local key = pandoc.utils.stringify(args[1])
    local _, unit, lesson = lookup(key)
    if not unit then
      return link(key, key)
    end
    if args[2] then
      return link(key, pandoc.utils.stringify(args[2]))
    end
    return link(key, "Unit " .. unit .. ", lesson " .. lesson)
  end,
}
