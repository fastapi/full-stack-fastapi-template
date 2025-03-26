from sentry_sdk import configure_scope
from sentry_sdk.hub import Hub
from sentry_sdk.integrations import Integration
from sentry_sdk.utils import capture_internal_exceptions

from sentry_sdk._types import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from typing import Optional

    from sentry_sdk._types import Event, Hint


class SparkIntegration(Integration):
    identifier = "spark"

    @staticmethod
    def setup_once():
        # type: () -> None
        patch_spark_context_init()


def _set_app_properties():
    # type: () -> None
    """
    Set properties in driver that propagate to worker processes, allowing for workers to have access to those properties.
    This allows worker integration to have access to app_name and application_id.
    """
    from pyspark import SparkContext

    spark_context = SparkContext._active_spark_context
    if spark_context:
        spark_context.setLocalProperty("sentry_app_name", spark_context.appName)
        spark_context.setLocalProperty(
            "sentry_application_id", spark_context.applicationId
        )


def _start_sentry_listener(sc):
    # type: (Any) -> None
    """
    Start java gateway server to add custom `SparkListener`
    """
    from pyspark.java_gateway import ensure_callback_server_started

    gw = sc._gateway
    ensure_callback_server_started(gw)
    listener = SentryListener()
    sc._jsc.sc().addSparkListener(listener)


def patch_spark_context_init():
    # type: () -> None
    from pyspark import SparkContext

    spark_context_init = SparkContext._do_init

    def _sentry_patched_spark_context_init(self, *args, **kwargs):
        # type: (SparkContext, *Any, **Any) -> Optional[Any]
        init = spark_context_init(self, *args, **kwargs)

        if Hub.current.get_integration(SparkIntegration) is None:
            return init

        _start_sentry_listener(self)
        _set_app_properties()

        with configure_scope() as scope:

            @scope.add_event_processor
            def process_event(event, hint):
                # type: (Event, Hint) -> Optional[Event]
                with capture_internal_exceptions():
                    if Hub.current.get_integration(SparkIntegration) is None:
                        return event

                    event.setdefault("user", {}).setdefault("id", self.sparkUser())

                    event.setdefault("tags", {}).setdefault(
                        "executor.id", self._conf.get("spark.executor.id")
                    )
                    event["tags"].setdefault(
                        "spark-submit.deployMode",
                        self._conf.get("spark.submit.deployMode"),
                    )
                    event["tags"].setdefault(
                        "driver.host", self._conf.get("spark.driver.host")
                    )
                    event["tags"].setdefault(
                        "driver.port", self._conf.get("spark.driver.port")
                    )
                    event["tags"].setdefault("spark_version", self.version)
                    event["tags"].setdefault("app_name", self.appName)
                    event["tags"].setdefault("application_id", self.applicationId)
                    event["tags"].setdefault("master", self.master)
                    event["tags"].setdefault("spark_home", self.sparkHome)

                    event.setdefault("extra", {}).setdefault("web_url", self.uiWebUrl)

                return event

        return init

    SparkContext._do_init = _sentry_patched_spark_context_init


class SparkListener(object):
    def onApplicationEnd(self, applicationEnd):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onApplicationStart(self, applicationStart):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onBlockManagerAdded(self, blockManagerAdded):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onBlockManagerRemoved(self, blockManagerRemoved):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onBlockUpdated(self, blockUpdated):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onEnvironmentUpdate(self, environmentUpdate):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onExecutorAdded(self, executorAdded):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onExecutorBlacklisted(self, executorBlacklisted):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onExecutorBlacklistedForStage(  # noqa: N802
        self, executorBlacklistedForStage  # noqa: N803
    ):
        # type: (Any) -> None
        pass

    def onExecutorMetricsUpdate(self, executorMetricsUpdate):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onExecutorRemoved(self, executorRemoved):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onJobEnd(self, jobEnd):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onJobStart(self, jobStart):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onNodeBlacklisted(self, nodeBlacklisted):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onNodeBlacklistedForStage(self, nodeBlacklistedForStage):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onNodeUnblacklisted(self, nodeUnblacklisted):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onOtherEvent(self, event):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onSpeculativeTaskSubmitted(self, speculativeTask):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onStageCompleted(self, stageCompleted):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onStageSubmitted(self, stageSubmitted):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onTaskEnd(self, taskEnd):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onTaskGettingResult(self, taskGettingResult):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onTaskStart(self, taskStart):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    def onUnpersistRDD(self, unpersistRDD):  # noqa: N802,N803
        # type: (Any) -> None
        pass

    class Java:
        implements = ["org.apache.spark.scheduler.SparkListenerInterface"]


class SentryListener(SparkListener):
    def __init__(self):
        # type: () -> None
        self.hub = Hub.current

    def onJobStart(self, jobStart):  # noqa: N802,N803
        # type: (Any) -> None
        message = "Job {} Started".format(jobStart.jobId())
        self.hub.add_breadcrumb(level="info", message=message)
        _set_app_properties()

    def onJobEnd(self, jobEnd):  # noqa: N802,N803
        # type: (Any) -> None
        level = ""
        message = ""
        data = {"result": jobEnd.jobResult().toString()}

        if jobEnd.jobResult().toString() == "JobSucceeded":
            level = "info"
            message = "Job {} Ended".format(jobEnd.jobId())
        else:
            level = "warning"
            message = "Job {} Failed".format(jobEnd.jobId())

        self.hub.add_breadcrumb(level=level, message=message, data=data)

    def onStageSubmitted(self, stageSubmitted):  # noqa: N802,N803
        # type: (Any) -> None
        stage_info = stageSubmitted.stageInfo()
        message = "Stage {} Submitted".format(stage_info.stageId())
        data = {"attemptId": stage_info.attemptId(), "name": stage_info.name()}
        self.hub.add_breadcrumb(level="info", message=message, data=data)
        _set_app_properties()

    def onStageCompleted(self, stageCompleted):  # noqa: N802,N803
        # type: (Any) -> None
        from py4j.protocol import Py4JJavaError  # type: ignore

        stage_info = stageCompleted.stageInfo()
        message = ""
        level = ""
        data = {"attemptId": stage_info.attemptId(), "name": stage_info.name()}

        # Have to Try Except because stageInfo.failureReason() is typed with Scala Option
        try:
            data["reason"] = stage_info.failureReason().get()
            message = "Stage {} Failed".format(stage_info.stageId())
            level = "warning"
        except Py4JJavaError:
            message = "Stage {} Completed".format(stage_info.stageId())
            level = "info"

        self.hub.add_breadcrumb(level=level, message=message, data=data)
